# Ports and Protocols You Should Know

An IP address gets a packet to the right machine. A port number gets it to the right program on that machine. Without ports, your web browser and your SSH client would be fighting over the same incoming stream of data. Ports are how one IP address can handle dozens of simultaneous, distinct conversations.

## What a Port Actually Is

A port is a 16-bit number, so it ranges from 0 to 65535. When your browser requests a page, it attaches a destination port (443 for HTTPS) and a randomly chosen source port so the server knows where to send the reply. The combination of source IP, source port, destination IP, and destination port uniquely identifies a connection. That's how a single machine can have hundreds of open TCP connections at once without mixing them up.

Ports don't exist in hardware. They're a transport-layer concept maintained by the OS. When a process wants to receive traffic, it binds to a port by asking the kernel to associate that port number with a socket.

## TCP vs UDP

Both TCP and UDP use port numbers, but they behave differently.

**TCP** establishes a connection before any data moves. The three-way handshake (SYN, SYN-ACK, ACK) confirms both sides are ready. TCP guarantees delivery and ordering, which is why it's used for anything where data integrity matters: web traffic, email, file transfers, remote shells.

**UDP** skips the handshake entirely. Packets go out with no acknowledgment and no guarantee they arrive. That's acceptable for DNS (a single question that fits in one packet), DHCP, video streaming, and games where a dropped frame is better than a late one.

Whether a given port is TCP, UDP, or both depends on the protocol running on it. Many services use the same port number on both, but that doesn't mean both transports make sense for that service.

## Port Ranges

The 65536 available ports are divided into three categories by IANA (the Internet Assigned Numbers Authority):

| Range | Name | Notes |
|-------|------|-------|
| 0 to 1023 | Well-known ports | Reserved for standard system services; binding requires root/admin on most OSes |
| 1024 to 49151 | Registered ports | Assigned to specific applications by IANA on request |
| 49152 to 65535 | Dynamic/ephemeral ports | Used by clients as temporary source ports for outbound connections |

When your browser connects to a server, it grabs an ephemeral port from the dynamic range as its source port. That's the address the server sends responses back to.

## The Ports Worth Knowing

These are the ports that come up constantly in networking, security work, and penetration testing.

| Port(s) | Protocol | Transport | Notes |
|---------|----------|-----------|-------|
| 20 | FTP data | TCP | Active mode data transfer channel |
| 21 | FTP control | TCP | Commands and authentication |
| 22 | SSH | TCP | Encrypted remote shell; also used by SCP and SFTP |
| 23 | Telnet | TCP | Plaintext remote shell; effectively obsolete |
| 25 | SMTP | TCP | Mail transfer between servers |
| 53 | DNS | TCP/UDP | UDP for queries; TCP for large responses and zone transfers |
| 67 | DHCP server | UDP | Server listens here to assign IP leases |
| 68 | DHCP client | UDP | Client receives lease response here |
| 80 | HTTP | TCP | Unencrypted web traffic |
| 110 | POP3 | TCP | Email retrieval; downloads and typically deletes from server |
| 123 | NTP | UDP | Clock synchronization |
| 143 | IMAP | TCP | Email retrieval; keeps mail on the server, supports folders |
| 161 | SNMP | UDP | Network device monitoring and management |
| 389 | LDAP | TCP | Directory services, including Active Directory |
| 443 | HTTPS | TCP | HTTP over TLS |
| 445 | SMB | TCP | Windows file sharing; also the port targeted by EternalBlue and WannaCry |
| 587 | SMTP submission | TCP | Authenticated email from client to server |
| 636 | LDAPS | TCP | LDAP over TLS |
| 993 | IMAPS | TCP | IMAP over TLS |
| 995 | POP3S | TCP | POP3 over TLS |
| 1433 | MSSQL | TCP | Microsoft SQL Server |
| 3306 | MySQL | TCP | MySQL and MariaDB |
| 3389 | RDP | TCP | Windows Remote Desktop Protocol |
| 5432 | PostgreSQL | TCP | PostgreSQL database |
| 5985 | WinRM HTTP | TCP | Windows Remote Management; used by PowerShell remoting |
| 6379 | Redis | TCP | Often exposed with no authentication in default configurations |
| 8080 | HTTP-alt | TCP | Common for dev servers, proxies, and apps that can't bind to port 80 |
| 8443 | HTTPS-alt | TCP | Alternative HTTPS port |
| 27017 | MongoDB | TCP | Also frequently exposed without authentication |

A few of these deserve special mention. Port 445 (SMB) has a long history of critical vulnerabilities. EternalBlue, the NSA-developed exploit that powered WannaCry in 2017, targeted SMB on port 445. If that port is reachable from the internet on a Windows machine, that's a serious problem. Redis (6379) and MongoDB (27017) show up constantly in breach reports because default configurations often require no password, and developers expose them to the internet anyway.

Port 23 (Telnet) still exists on a lot of embedded and industrial devices. Everything sent over Telnet is plaintext, including passwords. If you see it open during a scan, treat it as a finding.

## Why Attackers Care About Ports

Port scanning is typically one of the first steps in any reconnaissance phase. By probing which ports are open, an attacker learns what services are running. An open port 22 means SSH. Port 3389 means Windows RDP. Port 1433 means SQL Server. Each open port is a potential entry point, and each service has its own set of known vulnerabilities, default credentials, and misconfigurations.

This is called service fingerprinting. Tools like Nmap can go further than just detecting open ports; they probe each service to identify the specific software and version. A banner reading `OpenSSH 7.4` maps directly to a set of CVEs. That version was released in 2016 and has several known issues. The attacker didn't need to guess. The service told them.

The attack surface of a machine is roughly proportional to the number of services running on it. Every open port is a listener waiting for input, and every listener is an opportunity for something to go wrong.

## Non-Standard Ports Are Not Security

A common response to brute-force noise on port 22 is to move SSH to a different port, like 2222 or 22222. This does reduce log volume from automated scanners, which mostly target well-known ports. But it is not a security measure.

Anyone running a thorough scan will find it. Nmap's `-p-` flag scans all 65535 ports. A determined attacker takes maybe a few minutes longer. What you've accomplished is making it marginally less convenient, not meaningfully harder to compromise.

This is the definition of security through obscurity: relying on an attacker not knowing where something is, rather than making it actually resistant to attack. The right approach is to restrict access with firewall rules, require strong authentication (keys instead of passwords for SSH), and disable services you don't need. Moving SSH to port 2222 while leaving it accessible from anywhere with password authentication enabled is not progress.

Knowing which ports correspond to which services, and which of those services have a rough history, is one of the more practical things in this field. When you're reading a scan result or reviewing a firewall ruleset, the ports tell you exactly what you're dealing with.
