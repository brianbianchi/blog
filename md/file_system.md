# Linux File System

Follows the [Filesystem Hierarchy Standard (FHS)](https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard).

- Paths use forward slashes: `/`
- Case-sensitive: `File.txt` ≠ `file.txt`
- Hidden files start with `.` (e.g., `.bashrc`)

## Directory Map

```
/
├── bin        → Essential binaries (ls, cat, grep) — symlink to /usr/bin on modern distros
├── boot       → Kernel and bootloader files
├── dev        → Device files (block, char, pseudo-devices like /dev/null)
├── etc        → System-wide config files
├── home       → User home directories (/home/alice, /home/bob)
├── lib        → Shared libraries for /bin and /sbin
├── media      → Auto-mounted removable media (USB, CD)
├── mnt        → Temporary manual mount point
├── opt        → Optional third-party software
├── proc       → Virtual FS — live kernel and process info (not on disk)
├── root       → Root user's home directory
├── run        → Runtime data in RAM (PIDs, sockets) — cleared on reboot
├── sbin       → System admin binaries — symlink to /usr/sbin on modern distros
├── srv        → Data served by web/FTP services
├── sys        → Virtual FS — kernel device and driver interface
├── tmp        → Temporary files, cleared on reboot
├── usr        → User-installed apps, libraries, docs
│   ├── bin    → Most user commands live here
│   ├── lib    → Libraries for /usr/bin
│   └── share  → Architecture-independent data
└── var        → Variable data: logs (/var/log), mail, caches, spool
```

## File Permissions

```
-rwxr-xr--  1  alice  staff  4096  May 1  file.txt
 ^^^  ^^^  ^^^
 │    │    └── other: read only
 │    └─────── group: read + execute
 └──────────── owner: read + write + execute
```

First character: `-` file, `d` directory, `l` symlink, `b` block device, `c` char device.

Each permission set: `r` (4) `w` (2) `x` (1). Octal notation combines them: `rwxr-xr--` = 754.

```bash
chmod 755 file           # set permissions numerically
chmod u+x file           # add execute for owner
chown alice:staff file   # change owner and group
```

## Useful Commands

```bash
ls -la                              # list with hidden files and details
find / -name "*.conf" 2>/dev/null   # find files by name
file <path>                         # identify file type
stat <path>                         # detailed metadata
lsof -p <pid>                       # files open by a process
df -h                               # disk space by mount point
du -sh *                            # size of each item in current dir
```
