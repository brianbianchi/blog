# Understanding the Linux File System

This system follows a logical layout defined by the [Filesystem Hierarchy Standard (FHS)](https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard), maintained by the Linux Foundation. 

## Important Features

- **Forward slashes (`/`)** are used in paths instead of Windows’ backslashes (`\`).  
- **Linux is case-sensitive:** `File.txt` and `file.txt` are different files.  
- **Hidden files** start with a period (`.`) — for instance, `.bashrc`.  

***

### A Visual Map of the Linux File System  

```
/
├── bin        → Essential command binaries (e.g., ls, cat, grep)
├── boot       → Boot loader and kernel files
├── dev        → Device files (hardware access)
├── etc        → System configuration files
├── home       → User home directories
│   ├── alice
│   └── bob
├── lib        → Shared libraries for binaries
├── media      → Auto-mounted removable media (USB, CD)
├── mnt        → Temporary mount point for manual mounting
├── opt        → Optional third-party software
├── proc       → Virtual info about running processes
├── root       → Root user’s home directory
├── run        → Runtime data stored in RAM
├── sbin       → System binaries for admin tasks
├── snap       → Snap package location (Ubuntu-based)
├── srv        → Data served by network services (web/FTP)
├── sys        → Kernel device and driver interface
├── tmp        → Temporary files
├── usr        → User-installed applications and resources
└── var        → Variable data like logs and caches
```

***