# Lateral Movement Techniques

Initial access rarely lands you where you want to be. You might pop a foothold on an intern's workstation, a web server in a DMZ, or a jump box with limited reach. Lateral movement is how you get from there to the domain controller, the file server, the database, or whatever the actual target is.

This post covers the most common Windows lateral movement techniques, what artifacts they leave, and what to consider when choosing between them.

---

## Why It Matters

In a real network, the most sensitive data and systems are rarely at the edge. A phishing attack hits a regular user. A web vulnerability lands you on a web server. From there, you need to move. Understanding lateral movement is essential both for offensive work and for defenders trying to understand what post-exploitation looks like on their network.

---

## Pass-the-Hash (Brief Recap)

Pass-the-Hash (PtH) is covered in depth in its own post, so just a quick note here. NTLM authentication accepts a password hash directly, so if you've extracted a hash from LSASS or a SAM database, you can authenticate as that user without knowing the plaintext password.

Most of the tools covered below support pass-the-hash natively.

```bash
# Impacket generic example
psexec.py domain/user@target -hashes :NTLMhash
```

---

## PsExec

PsExec is the classic Windows lateral movement technique. It works by:

1. Uploading a small service binary to the target's `ADMIN$` share (which maps to `C:\Windows\`)
2. Using the Windows Service Control Manager (SCM) to register and start that service
3. The service creates a named pipe that you interact with, giving you a SYSTEM-level shell

The legitimate Sysinternals PsExec does this. Impacket's `psexec.py` reimplements the same approach:

```bash
psexec.py domain/user:password@target
psexec.py domain/user@target -hashes :NTLMhash
```

The output you get is a SYSTEM shell, which is useful. But PsExec is loud. It writes a binary to disk, creates a Windows service with a random-looking name, and generates several Windows event log entries (7045 for new service install, 4624 for logon). Any halfway decent EDR will catch it. Use it in CTFs and lab environments without hesitation; be more careful in real engagements.

---

## WMI (Windows Management Instrumentation)

WMI is a built-in Windows management framework that allows remote command execution. It's been part of Windows for decades and is heavily used for legitimate administration, which is part of why it's attractive to attackers.

Impacket's `wmiexec.py` uses WMI to execute commands remotely:

```bash
wmiexec.py domain/user:password@target
wmiexec.py domain/user@target -hashes :NTLMhash
```

The difference from PsExec is meaningful. WMI execution is "semi-fileless": commands run through WMI don't require writing a binary to disk in the same way. Output is written to a temporary file on the target, but the execution itself doesn't create a persistent service.

You can also invoke WMI directly through PowerShell:

```powershell
Invoke-WmiMethod -ComputerName target -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c whoami > C:\output.txt"
```

WMI logs to `Microsoft-Windows-WMI-Activity/Operational` and generates 4624 logon events, but it's quieter than PsExec overall.

---

## WinRM / Evil-WinRM

WinRM (Windows Remote Management) is Microsoft's implementation of the WS-Management protocol. PowerShell remoting runs on top of it. It listens on port 5985 (HTTP) and 5986 (HTTPS).

If WinRM is enabled on a target and you have credentials (or a hash), you can get an interactive PowerShell session:

```bash
evil-winrm -i target -u user -p password
evil-winrm -i target -u user -H NTLMhash
```

Evil-WinRM is a Ruby tool built specifically for penetration testing that wraps WinRM with useful features like file upload/download, passing the hash, and loading PowerShell scripts directly into memory.

WinRM is not enabled by default on workstations but is commonly enabled on servers. Domain controllers always have it enabled. The lateral movement requires your account to be in the Remote Management Users group or local administrators on the target.

---

## SMB Lateral Movement

Beyond PsExec-style service execution, SMB can be used in simpler ways.

If you have access to an `ADMIN$`, `C$`, or other admin share, you can copy files directly to the target system. Combine this with a scheduled task or service creation:

```bash
# List shares
smbclient -L //target -U user%password

# Copy a payload to the target
smbclient //target/C$ -U user%password -c "put shell.exe Windows\Temp\shell.exe"
```

Then trigger execution via `sc`, `schtasks`, WMI, or another mechanism.

`smbexec.py` from Impacket takes a slightly different approach than `psexec.py`: instead of uploading a binary and creating a persistent service, it creates a service that runs your command directly and then deletes itself. Somewhat noisier in some ways, less noisy in others.

---

## RDP

RDP (Remote Desktop Protocol) is port 3389. If it's enabled on the target and you have valid credentials, you can get a full graphical session.

From Linux:

```bash
xfreerdp /u:user /p:password /v:target:3389
remmina rdp://user:password@target
```

If you've already compromised a system and want to enable RDP on it:

```cmd
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f
netsh advfirewall firewall add rule name="RDP" protocol=TCP dir=in localport=3389 action=allow
```

Add a user to the Remote Desktop Users group:

```cmd
net localgroup "Remote Desktop Users" hacker /add
```

RDP generates detailed logs (event IDs 4624, 4778, 4779) and is visible in the network. But if the environment already uses RDP heavily, additional connections blend in more easily than a PsExec service install.

Pass-the-Hash with RDP is possible on Windows 8.1+ with Restricted Admin mode enabled:

```bash
xfreerdp /u:user /pth:NTLMhash /v:target /cert-ignore
```

---

## DCOM

DCOM (Distributed COM) allows invoking COM objects on remote machines. Several COM objects support methods that execute code. This is less commonly used than WMI or WinRM but worth knowing.

Two well-known objects used for lateral movement:

**MMC20.Application:**

```powershell
$com = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","target"))
$com.Document.ActiveView.ExecuteShellCommand("cmd.exe",$null,"/c calc.exe","7")
```

**ShellBrowserWindow:**

```powershell
$com = [activator]::CreateInstance([type]::GetTypeFromProgID("Shell.Application","target"))
$com.ShellExecute("cmd.exe","/c calc.exe","","",0)
```

DCOM uses RPC and dynamic ports, and requires the target to have DCOM enabled (it is by default) and your account to have appropriate permissions. Detection is harder than PsExec since there's no service creation event, but process creation logs and RPC traffic analysis can catch it.

---

## Token Impersonation

If you're running in a process on a machine and higher-privileged users are also logged into that machine, you may be able to steal their security tokens and impersonate them.

In Meterpreter:

```
use incognito
list_tokens -u
impersonate_token "DOMAIN\\Administrator"
```

This works when:
- Your process has `SeImpersonatePrivilege` or `SeDebugPrivilege`
- The target user has a token active in a process you can access

Token impersonation is local, not a network lateral movement technique, but it's often a bridge: you escalate on a machine via token theft, then use those elevated credentials to move laterally to another system.

---

## Artifacts and Detection Considerations

Not all lateral movement techniques are equal from a visibility standpoint.

| Technique | Writes to disk | Creates service | Network port | Log events |
|-----------|---------------|----------------|-------------|-----------|
| PsExec | Yes (service binary) | Yes | SMB (445) | 7045, 4624, 4648 |
| wmiexec | Minimal (output file) | No | WMI/RPC | 4624, WMI logs |
| WinRM / Evil-WinRM | No | No | 5985/5986 | 4624, PowerShell logs |
| RDP | No | No | 3389 | 4624, 4778 |
| DCOM | No | No | RPC dynamic | 4624, process creation |
| SMB + schtasks | Yes (payload) | No (scheduled task) | SMB (445) | 4698, 4702 |

"Fileless" is relative. WMI and WinRM don't require you to drop a binary in the traditional sense, but if you're running PowerShell commands, those commands may be logged (Script Block Logging, Module Logging, Transcription logging). EDR products also monitor for suspicious process trees regardless of whether files are written to disk.

From a detection perspective, the most reliable signals are: logon type 3 (network logon) from unexpected source IPs, administrative share access (`ADMIN$`, `C$`), PowerShell remoting from non-admin workstations, and new service creation events on machines that don't typically get new services.

The practical takeaway for offensive work: if you're operating in an environment with mature EDR, PsExec is almost certainly going to get you caught. WMI and WinRM are quieter but not invisible. Blending in with the environment's normal tooling (if it's a PowerShell-heavy environment, PowerShell remoting looks more normal) is generally better than using techniques that stick out.
