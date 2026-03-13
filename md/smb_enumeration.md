# SMB Enumeration

SMB (Server Message Block) is a network file sharing protocol. It lets Windows machines share files, printers, and other resources across a network. You'll find it running on port 445, or on port 139 when it's operating over the older NetBIOS transport layer. Nearly every Windows machine on a corporate network has it running by default.

The reason SMB gets so much attention in security is a combination of ubiquity and history. It's everywhere, and it has a long track record of critical vulnerabilities being found in it.

## Why SMB Gets Targeted

In 2017, the Shadow Brokers leaked NSA exploit tools, including EternalBlue, which exploited MS17-010, a critical remote code execution vulnerability in SMBv1. WannaCry and NotPetya both used EternalBlue to spread themselves across networks at a scale that was genuinely alarming. Hundreds of thousands of machines infected within hours. Billions of dollars in damages. All because SMBv1 was still enabled on systems that hadn't been patched.

That specific vulnerability is old news now, but SMBv1 still shows up in the wild regularly. Embedded systems, legacy servers, medical devices, industrial control systems. Something running SMBv1 in 2025 is a red flag.

Beyond EternalBlue, SMB has historically been a source of credential exposure through NTLM relay attacks, unauthenticated enumeration of users and shares, and misconfigured guest access. It's a protocol that was designed for trusted networks and has been awkwardly extended to work in environments where trust can't be assumed.

## Null Sessions and Anonymous Access

A null session is an unauthenticated connection to the IPC$ share, a special administrative share used for inter-process communication. On older Windows systems (pre-Vista, and Server 2003 and earlier), null sessions allowed anonymous users to enumerate a remarkable amount of information: usernames, group memberships, share lists, password policies, even sometimes RID cycling to enumerate all accounts.

Modern Windows defaults are much more restrictive. But you still encounter null sessions on older systems and on Samba configurations that haven't been hardened. It's always worth checking.

## Tools and Techniques

### smbclient

`smbclient` is essentially an FTP-like client for SMB shares. The first thing you usually do with it is list available shares:

```
smbclient -L //192.168.1.10 -N
```

The `-N` flag means no password (attempting a null session). If the server allows anonymous listing, you'll see the shares. To connect to a specific share:

```
smbclient //192.168.1.10/share_name -N
```

Once connected, you can navigate with `ls`, `cd`, `get`, `put`, and `mget`. Finding a readable share is one thing; finding a writable one is much more interesting.

With valid credentials:

```
smbclient //192.168.1.10/share_name -U username
```

### smbmap

`smbmap` is purpose-built for enumerating shares and their permissions. It's faster than manually connecting to each share with `smbclient` and it clearly shows you read/write access.

```
# Null session
smbmap -H 192.168.1.10

# With credentials
smbmap -H 192.168.1.10 -u username -p password

# Enumerate recursively
smbmap -H 192.168.1.10 -u username -p password -R

# Look for specific file types
smbmap -H 192.168.1.10 -u username -p password -R -A '\.txt$'
```

The output shows each share alongside its access level: NO ACCESS, READ ONLY, or READ, WRITE.

### enum4linux

`enum4linux` is a wrapper around various Samba tools that tries to pull as much information as possible from a Windows or Samba host. It attempts to enumerate shares, users, groups, password policy, and OS information, with and without credentials.

```
enum4linux -a 192.168.1.10
```

The `-a` flag runs all checks. It's noisy and not particularly stealthy, but for an internal assessment it's a quick way to get a lot of information at once. The output can be verbose; pipe it to a file and grep for the interesting parts.

### CrackMapExec (CME)

CrackMapExec is more of a Swiss army knife than a single-purpose tool. For SMB enumeration it's excellent, and it scales well when you're working against an entire subnet rather than a single host.

```
# Enumerate hosts on a subnet (null session)
crackmapexec smb 192.168.1.0/24

# Enumerate with credentials
crackmapexec smb 192.168.1.0/24 -u username -p password

# List shares
crackmapexec smb 192.168.1.10 -u username -p password --shares

# Enumerate logged-on users
crackmapexec smb 192.168.1.10 -u username -p password --loggedon-users

# Dump SAM hashes (requires admin)
crackmapexec smb 192.168.1.10 -u username -p password --sam
```

CME also color-codes results. Green means the credentials worked; red means they didn't. When you're spraying credentials across a subnet, this makes the output immediately readable.

### rpcclient

`rpcclient` lets you interact with the RPC (Remote Procedure Call) endpoint on Windows systems. It's useful for enumerating users and groups when other tools come up short.

```
# Connect with null session
rpcclient -U "" -N 192.168.1.10

# Once connected, useful commands:
enumdomusers        # list all domain users
enumdomgroups       # list domain groups
querydominfo        # domain info and password policy
querydispinfo       # more user details
queryuser 0x1f4     # query a specific user by RID
```

RID cycling is worth knowing: Windows assigns RIDs (Relative Identifiers) sequentially starting at 500 for the Administrator account. By iterating through RIDs with `queryuser`, you can enumerate all accounts even if direct enumeration is restricted.

```
for i in $(seq 500 1100); do
    rpcclient -U "" -N 192.168.1.10 -c "queryuser $i" 2>/dev/null | grep "User Name"
done
```

## What to Look For

**Open guest shares** are shares accessible without credentials, often containing files that were never intended to be public. Configuration files, scripts, backups, and documents with embedded credentials are common finds.

**Writable shares** matter because writing a file to a share can enable more sophisticated attacks. Dropping a malicious `.lnk` file or `desktop.ini` into a share that users browse can capture NTLM hashes when someone opens the folder.

**SMBv1 still enabled** is a vulnerability finding in itself, regardless of patching status. The recommendation has been to disable it entirely for years. Seeing it active in a modern environment is a sign of poor hygiene.

**Weak or non-existent password policies** surfaced through `querydominfo` or `enum4linux` tell you what kind of brute-force is feasible.

**OS version from banner** lets you know exactly what you're dealing with. Windows Server 2008 R2 in 2025 means you're almost certainly looking at an unpatched system with a decade of vulnerabilities on it.

## SMB Signing

SMB signing is a security feature that cryptographically signs SMB traffic so that the communicating parties can verify it hasn't been tampered with in transit. When it's enforced, NTLM relay attacks don't work.

When SMB signing is disabled or not required, an attacker who can intercept network traffic can relay captured NTLM authentication attempts to other machines. The classic attack chain: capture an NTLM authentication attempt (through a rogue responder, a malicious link, or a coercion attack), relay it to another machine that trusts that credential, and gain authenticated access without ever cracking the password.

Tools like `crackmapexec` report SMB signing status in their output. Seeing `signing: False` across a subnet is a significant finding.

```
crackmapexec smb 192.168.1.0/24 --gen-relay-list unsigned_hosts.txt
```

That command builds a list of all hosts with SMB signing not enforced, ready to feed into a relay attack.

## Summary

| Tool | Best For |
|------|---------|
| `smbclient` | Browsing and interacting with shares |
| `smbmap` | Quick share enumeration with permissions |
| `enum4linux` | Bulk enumeration of users, groups, policy |
| `crackmapexec` | Large-scale scanning, credential testing |
| `rpcclient` | Manual RPC interaction, user enumeration |

SMB enumeration is a standard part of any internal assessment. The combination of broad deployment, legacy configurations, and a history of severe vulnerabilities makes it consistently productive. Even on hardened modern environments, you'll often find at least one misconfigured share or a host with signing disabled.
