# How Kerberos Works (and Gets Abused)

Kerberos is the authentication backbone of Active Directory. If you're doing anything with Windows enterprise environments, you need to understand it, both how it's supposed to work and the several ways attackers bend it to their purposes. This post covers the protocol from first principles and then walks through the main attack categories.

---

## Why Kerberos Exists

Before Kerberos, Windows networks relied heavily on NTLM. NTLM has some significant problems: it's vulnerable to pass-the-hash attacks, it involves sending authentication material over the network in ways that can be captured and cracked, and it provides no mutual authentication (the client can't verify the server is who it claims to be).

Kerberos solves this with a ticket-based system. The core idea: you prove your identity once to a trusted third party, get a ticket, and use that ticket to access services without re-sending your credentials each time. The password itself never travels over the network during normal operation.

---

## Key Components

| Component | What it is |
|-----------|-----------|
| KDC (Key Distribution Center) | The central authority. In Active Directory, this runs on every domain controller. |
| AS (Authentication Service) | The part of the KDC that handles initial authentication and issues TGTs. |
| TGS (Ticket Granting Service) | The part of the KDC that issues service tickets in exchange for a valid TGT. |
| TGT (Ticket Granting Ticket) | A ticket that proves you've authenticated. Used to request service tickets without re-entering your password. |
| Service Ticket (ST) | A ticket for a specific service. You present this to the service to gain access. |
| krbtgt | The special domain account whose password is used to encrypt and sign TGTs. More on this below. |

The KDC knows the password (or rather, the password hash) of every account in the domain. This is what makes the whole system work.

---

## The Authentication Flow

Here's what actually happens when a user logs in and accesses a network resource.

### Step 1: AS-REQ / AS-REP (Getting a TGT)

The client sends an AS-REQ to the Authentication Service. This request includes the username and a timestamp encrypted with the user's password hash. This encrypted timestamp proves the client knows the password without sending the password itself. This is Kerberos pre-authentication.

The KDC looks up the user's password hash, attempts to decrypt the timestamp, and verifies it's recent. If everything checks out, it responds with an AS-REP containing:

- A TGT encrypted with the `krbtgt` account's hash (the client cannot decrypt this)
- A session key encrypted with the user's password hash (the client can decrypt this)

The client now holds a TGT it can't read or modify (it's encrypted with a key the client doesn't have), plus a session key for communicating with the TGS.

### Step 2: TGS-REQ / TGS-REP (Getting a Service Ticket)

When the client wants to access a service (say, a file share), it sends a TGS-REQ to the Ticket Granting Service. This request contains the TGT and the name of the service the client wants to access, expressed as an SPN (Service Principal Name).

The TGS decrypts the TGT (it can do this because it has the `krbtgt` hash), verifies it's valid, and issues a service ticket. The service ticket is encrypted with the target service account's hash. The client cannot read this ticket either.

### Step 3: AP-REQ (Accessing the Service)

The client sends the service ticket to the target service in an AP-REQ. The service decrypts it using its own account's hash, verifies the client's identity and authorization, and grants access.

The beautiful part of this design: at no point does the client's password travel over the network. The KDC trusts the client because they could only produce the encrypted timestamp if they knew the password. Services trust the KDC because only the KDC could have encrypted the service ticket correctly.

---

## The krbtgt Account

The `krbtgt` account is the most sensitive account in an Active Directory domain. Its hash is the key used to encrypt and sign every TGT in the domain. If an attacker gets the `krbtgt` hash, they can forge TGTs for any user, including domain admins, with any privileges they want. This is the Golden Ticket attack (covered below).

The `krbtgt` account's password is rarely changed manually, and some organizations have never changed it since the domain was created. Because of this, a compromised `krbtgt` hash can persist for years if nobody notices.

---

## Kerberoasting

Kerberoasting is one of the most commonly used Active Directory attacks, and it works because of a quirk in how service tickets are encrypted.

Any domain user can request a service ticket for any service registered in the domain (identified by its SPN). The TGS-REP response contains a service ticket encrypted with the service account's NTLM hash. You can take that encrypted ticket offline and crack it, trying to recover the service account's plaintext password.

The reason this works: many service accounts have weak passwords, especially older accounts that predate modern password policies. And the request for a service ticket is completely legitimate and nearly indistinguishable from normal traffic.

### How to Kerberoast

Using Impacket on Linux:

```bash
GetUserSPNs.py domain.local/username:password -dc-ip 10.10.10.10 -request
```

Using Rubeus on Windows:

```cmd
Rubeus.exe kerberoast /outfile:hashes.txt
```

The output is a hash in `$krb5tgs$23$...` format. Crack it with Hashcat:

```bash
hashcat -m 13100 hashes.txt wordlist.txt
```

The attack is most effective against:
- Service accounts with SPNs and weak passwords
- Accounts using RC4 encryption (type 23) rather than AES (type 18 or 17), since RC4 hashes crack faster

### Defenses

Use long, random service account passwords (managed service accounts and group managed service accounts do this automatically). Monitor for a single user requesting service tickets for many SPNs in a short period.

---

## AS-REP Roasting

Similar to Kerberoasting but targets accounts with Kerberos pre-authentication disabled.

When pre-authentication is disabled on an account, anyone can send an AS-REQ for that user and receive an AS-REP without providing any credentials. The AS-REP response includes data encrypted with the user's password hash. You get that encrypted blob without even knowing any credentials, and you crack it offline.

### How to AS-REP Roast

Using Impacket (no credentials needed):

```bash
GetNPUsers.py domain.local/ -usersfile users.txt -no-pass -dc-ip 10.10.10.10
```

Or with valid credentials to enumerate which accounts are vulnerable:

```bash
GetNPUsers.py domain.local/username:password -dc-ip 10.10.10.10 -request
```

Using Rubeus:

```cmd
Rubeus.exe asreproast /outfile:asrephashes.txt
```

Crack with Hashcat (mode 18200):

```bash
hashcat -m 18200 asrephashes.txt wordlist.txt
```

Pre-authentication disabled is an unusual setting and most accounts won't have it. But it does appear in the wild, sometimes deliberately (older applications requiring it) and sometimes by accident.

---

## Pass-the-Ticket

Instead of cracking a ticket to get a password, Pass-the-Ticket involves exporting Kerberos tickets from memory and importing them into another session to impersonate a user.

Using Mimikatz:

```
# Export all tickets from LSASS memory
sekurlsa::tickets /export

# Import a ticket into the current session
kerberos::ptt ticket.kirbi
```

This is useful when you have a high-privileged user's ticket in memory on a machine you've compromised. You can import their TGT and then request service tickets as them, accessing resources they have rights to.

Tickets are time-limited (default TGT lifetime is 10 hours, renewable for 7 days), so Pass-the-Ticket isn't persistent. But within that window, it's effective.

---

## Golden Ticket

The most powerful Kerberos attack. If you have the `krbtgt` hash, you can forge any TGT for any user with any group memberships you choose. Because the KDC trusts TGTs it can verify were signed with the `krbtgt` key, a forged TGT is treated as completely legitimate.

### What you need

- Domain name
- Domain SID
- `krbtgt` NTLM hash
- Target username (or just make one up)

Obtain the `krbtgt` hash via DCSync (if you have replication privileges) or by running Mimikatz on a domain controller.

```
# DCSync with Mimikatz (requires replication privileges)
lsadump::dcsync /domain:domain.local /user:krbtgt

# Or if you have shell on the DC
lsadump::lsa /patch
```

### Creating the golden ticket

```
# With Mimikatz
kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-... /krbtgt:<hash> /ticket:golden.kirbi

# Import it
kerberos::ptt golden.kirbi
```

Using Impacket:

```bash
ticketer.py -nthash <krbtgt hash> -domain-sid S-1-5-21-... -domain domain.local Administrator
export KRB5CCNAME=Administrator.ccache
secretsdump.py -k -no-pass dc.domain.local
```

### Why Golden Tickets are dangerous

The attacker can create tickets for any user, including users that don't exist. They can set group memberships to include Domain Admins. The default ticket lifetime in a forged ticket can be set to years. And crucially, these tickets survive password changes on every account except `krbtgt` itself. The only way to invalidate all outstanding golden tickets is to change the `krbtgt` password twice (since old tickets reference the previous password, you need two rotations to push out the previous one).

Golden tickets are persistence mechanisms as much as they are attack vectors.

---

## Silver Ticket

A Silver Ticket is a forged service ticket rather than a forged TGT. Instead of the `krbtgt` hash, you forge a ticket using a specific service account's hash.

The difference: Silver Tickets don't go through the KDC at all. The service itself decrypts the ticket and trusts it. This means there's no KDC log entry for the authentication, making Silver Tickets harder to detect than Golden Tickets.

The trade-off is scope. A Silver Ticket is only valid for the specific service whose hash you used to forge it. If you compromise a web server's service account hash, you can forge tickets for that web service but not for file shares or other services.

```
kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-... /target:server.domain.local /service:cifs /rc4:<service account hash> /ticket:silver.kirbi
```

Useful for maintaining access to a specific service without touching the KDC, which is valuable in environments with good authentication logging.

---

## DCSync

DCSync isn't a Kerberos attack per se, but it's closely related to domain compromise and is how attackers obtain `krbtgt` hashes without having to log into a domain controller.

Domain controllers replicate password data between themselves using the Directory Replication Service (DRS) protocol. DCSync works by mimicking this replication request. If your account has the necessary replication privileges (`DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All`), you can request password data for any user from any domain controller without ever touching the DC's filesystem or running code on it.

By default, these replication privileges are held by Domain Admins, Enterprise Admins, and domain controllers. But administrators sometimes grant them to other accounts or groups for legitimate replication-related purposes, and that's an escalation path if you compromise one of those accounts.

```bash
# Impacket
secretsdump.py domain.local/admin:password@dc.domain.local

# Mimikatz
lsadump::dcsync /domain:domain.local /all /csv
```

The output includes NTLM hashes for every account in the domain, including `krbtgt`.

---

## Detection and Defenses

| Attack | Detection signals |
|--------|------------------|
| Kerberoasting | Spike in TGS requests from a single user for many different SPNs; requests for RC4 service tickets in environments that should be using AES |
| AS-REP Roasting | AS-REQ messages with no pre-authentication field; identify accounts with pre-auth disabled proactively |
| Pass-the-Ticket | Tickets used from unexpected IPs; anomalous ticket reuse patterns |
| Golden Ticket | Tickets with unusually long validity periods; tickets for users that don't exist; 4769 events with unexpected fields |
| Silver Ticket | Harder, since no KDC is involved; PAC validation (if enabled) can help |
| DCSync | Windows event 4662 with specific access rights; network traffic from non-DC sources performing DRS operations |

On the defensive side:
- Use managed service accounts (MSA/gMSA) for service accounts, which automatically rotate passwords and are resistant to Kerberoasting
- Enforce Kerberos pre-authentication on all accounts
- Limit replication privileges strictly
- Rotate the `krbtgt` password periodically (Microsoft has tooling for doing this safely)
- Enable Protected Users security group for high-privilege accounts, which among other things forces AES encryption and prevents credential caching
