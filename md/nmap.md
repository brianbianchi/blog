# Nmap: A Practical Guide

Nmap (Network Mapper) is probably the most widely used network scanning tool in existence. It maps out hosts on a network, discovers open ports, fingerprints services and operating systems, and can run scripts against targets to probe for specific vulnerabilities or configurations. Whether you're doing a penetration test, auditing your own infrastructure, or just trying to understand what's running on a network, Nmap is usually the first tool you reach for.

The basic syntax is simple:

```
nmap [options] [target]
```

The target can be a single IP, a hostname, a CIDR range like `192.168.1.0/24`, or a file containing a list of targets with `-iL`. Options control what kind of scan to run, how fast to run it, and what to do with the results.

## Scan Types

Understanding the different scan types matters because they behave differently on the wire and have different implications for stealth and accuracy.

### TCP Connect Scan (-sT)

This is the default scan when Nmap is run without root privileges. It completes the full three-way TCP handshake (SYN, SYN-ACK, ACK) and then immediately tears down the connection with a RST. Because it completes a full connection, it's reliably accurate. It's also the noisiest option: every open port shows up in the application logs of the target service.

```
nmap -sT 192.168.1.10
```

### SYN Scan (-sS)

The SYN scan, sometimes called a stealth scan or half-open scan, is the default when Nmap runs with root privileges. It sends a SYN, waits for a SYN-ACK from open ports (or a RST from closed ones), and then responds with a RST instead of completing the handshake. The connection never fully opens, which means many older logging systems won't record it. Modern firewalls and IDS absolutely will, but the name has stuck.

```
sudo nmap -sS 192.168.1.10
```

This is usually what you want for general scanning. It's faster than `-sT` and less likely to fill up logs.

### UDP Scan (-sU)

UDP is connectionless, which makes scanning it awkward. Nmap sends a UDP packet to each port. Closed ports typically return an ICMP "port unreachable" message. Open ports often respond with nothing at all, which Nmap marks as `open|filtered` because there's no way to tell without a response. This ambiguity, combined with ICMP rate limiting on most systems, makes UDP scanning painfully slow.

```
sudo nmap -sU 192.168.1.10
```

It's worth doing though. DNS (53), SNMP (161), TFTP (69), and NTP (123) are all UDP, and they're frequently misconfigured.

### NULL, FIN, and Xmas Scans

These three scans exploit a quirk in the TCP RFC: a packet sent to a closed port should get a RST back, but a packet sent to an open port should be silently dropped if it doesn't make sense (no SYN, no established session).

- **NULL scan (-sN):** sends a packet with no flags set
- **FIN scan (-sF):** sends only the FIN flag
- **Xmas scan (-sX):** sets FIN, PSH, and URG (lights up like a Christmas tree)

The theory is that these can bypass some stateless packet filters that only block SYN packets. In practice, they work reliably only against RFC-compliant TCP stacks. Windows systems don't follow this behavior and return RSTs regardless, making these scans useless against most Windows targets. They're more useful against Unix/Linux systems with simpler firewalls.

```
sudo nmap -sN 192.168.1.10
sudo nmap -sF 192.168.1.10
sudo nmap -sX 192.168.1.10
```

## Host Discovery

Before scanning ports, Nmap needs to know which hosts are actually alive. By default it sends ICMP echo requests, TCP SYN to port 443, TCP ACK to port 80, and ICMP timestamp requests. You can control this behavior directly.

### Ping Sweep (-sn)

The `-sn` flag tells Nmap to do host discovery only, with no port scan. This is useful for mapping out which IPs in a range are responding before you commit to a full port scan.

```
nmap -sn 192.168.1.0/24
```

### Skipping Ping (-Pn)

Some hosts don't respond to ICMP at all, either because it's firewalled or because they're configured that way. If you try to scan a host that drops pings, Nmap will assume it's down and skip it. The `-Pn` flag tells Nmap to skip host discovery entirely and just scan every IP as if it were alive.

```
nmap -Pn 10.10.10.5
```

Useful when you know a target is up but ICMP is blocked. The trade-off is that scans take longer since Nmap isn't pruning dead hosts first.

## Port Ranges

By default, Nmap scans the 1,000 most common ports. That covers a lot, but not everything.

| Flag | What it does |
|------|-------------|
| `-p 80` | Scan only port 80 |
| `-p 80,443,8080` | Scan specific ports |
| `-p 1-1000` | Scan a range |
| `-p-` | Scan all 65,535 ports |
| `--top-ports 100` | Scan the top N most common ports |

Full port scans with `-p-` take significantly longer but occasionally turn up services running on unusual ports. It's worth doing on high-value targets.

## Service and Version Detection (-sV)

An open port tells you something is listening. Service and version detection tries to figure out what. Nmap sends probes to open ports and analyzes the responses against its database of known service banners.

```
nmap -sV 192.168.1.10
```

The output changes from something like `80/tcp open http` to `80/tcp open http Apache httpd 2.4.41`. That version number matters: it's what you look up against CVE databases.

You can control how aggressively Nmap probes with `--version-intensity` (0-9). The default is 7. Lower values are faster but less thorough.

## OS Detection (-O)

Nmap can attempt to fingerprint the operating system of a remote host by analyzing TCP/IP stack behavior: things like window size, TTL values, TCP options, and how the host responds to various probe packets.

```
sudo nmap -O 192.168.1.10
```

OS detection requires at least one open and one closed port to work well. The results are probabilistic; Nmap will give you a confidence percentage. It's useful for reconnaissance but don't treat the output as ground truth.

Combining both detection flags is common:

```
sudo nmap -sV -O 192.168.1.10
```

Or just use `-A`, which enables OS detection, version detection, script scanning, and traceroute all at once.

## Nmap Scripting Engine (NSE)

The NSE is where Nmap goes from a port scanner to something genuinely powerful. Scripts are written in Lua and can do everything from grabbing HTTP titles to checking whether a host is vulnerable to specific CVEs.

### Running Default Scripts (-sC)

The `-sC` flag runs the default script set, which covers safe, generally useful checks: grabbing banners, extracting HTTP titles, checking for anonymous FTP login, enumerating SSL certificates, and similar reconnaissance tasks.

```
nmap -sC -sV 192.168.1.10
```

You'll see `-sC -sV` used together constantly. It's a sensible default for most scans.

### Script Categories

Scripts are organized into categories:

| Category | What it does |
|----------|-------------|
| `auth` | Tries authentication-related checks (anonymous access, default credentials) |
| `discovery` | Enumerates services for information |
| `vuln` | Checks for known vulnerabilities |
| `exploit` | Attempts actual exploitation (use carefully) |
| `safe` | Non-intrusive scripts unlikely to crash services |
| `intrusive` | More aggressive, may affect service stability |
| `brute` | Credential brute-force attacks |

Run all scripts in a category:

```
nmap --script vuln 192.168.1.10
nmap --script auth 192.168.1.10
```

### Example Scripts

A few scripts worth knowing by name:

**`http-title`** grabs the title tag from HTTP responses. Quick way to get a sense of what's running on web servers.

```
nmap --script http-title 192.168.1.10
```

**`smb-vuln-ms17-010`** checks whether a host is vulnerable to EternalBlue (the vulnerability behind WannaCry). This is the kind of thing you want to sweep your network for during an internal assessment.

```
nmap --script smb-vuln-ms17-010 192.168.1.10
```

**`ftp-anon`** checks whether anonymous FTP login is allowed. Still shockingly common on old network gear and legacy servers.

```
nmap --script ftp-anon 192.168.1.10
```

You can specify multiple scripts with commas, use wildcards, or combine categories:

```
nmap --script "http-*" 192.168.1.10
nmap --script "vuln,safe" 192.168.1.10
```

## Output Formats

Always save your scan results. Networks change, and being able to diff a scan from last week against one from today is genuinely useful.

| Flag | Format |
|------|--------|
| `-oN output.txt` | Normal (human-readable) |
| `-oX output.xml` | XML (parseable by other tools) |
| `-oG output.gnmap` | Grepable (easy to parse with grep/awk) |
| `-oA output` | All three formats at once, with appropriate extensions |

The `-oA` flag is the most convenient option when you want everything. It creates `output.nmap`, `output.xml`, and `output.gnmap` simultaneously.

## Timing Templates

Nmap has six timing presets that control how aggressively it probes targets.

| Template | Name | Description |
|----------|------|-------------|
| `-T0` | Paranoid | Extremely slow, one probe at a time with long delays. Designed to evade IDS. |
| `-T1` | Sneaky | Still very slow, minimal parallelism |
| `-T2` | Polite | Slows down to avoid overwhelming the target |
| `-T3` | Normal | The default |
| `-T4` | Aggressive | Assumes a reliable, fast network. Good for internal scans. |
| `-T5` | Insane | Maximum speed, will miss things on slow or congested networks |

For most internal assessments on a reliable LAN, `-T4` is a reasonable choice. On external targets over the internet, `-T3` or `-T4` both work fine. `-T5` will produce unreliable results if the network can't keep up.

## Practical Examples

Putting it all together, here are some common scan patterns:

**Quick host discovery on a subnet:**
```
nmap -sn 10.10.10.0/24
```

**Standard service scan with default scripts:**
```
sudo nmap -sC -sV -T4 10.10.10.5
```

**Full port scan followed by a targeted service scan:**
```
sudo nmap -p- --min-rate 5000 10.10.10.5 -oN full_ports.txt
sudo nmap -sC -sV -p 22,80,443,8080 10.10.10.5 -oN targeted.txt
```

**Vulnerability scan against a specific host:**
```
sudo nmap --script vuln 10.10.10.5 -oN vuln_scan.txt
```

**UDP scan for common services:**
```
sudo nmap -sU --top-ports 20 10.10.10.5
```

**Aggressive all-in-one scan:**
```
sudo nmap -A -T4 -p- 10.10.10.5 -oA full_scan
```

## A Word on Noise

Aggressive scans get detected. A `-T5` scan with `-A` against an external target is going to trigger IDS alerts. Even a careful SYN scan will show up in logs if someone is paying attention. The choice of scan type and timing isn't just a performance question; it's an operational one.

For red team work or testing against environments that have active monitoring, slow scans with randomized order (`--randomize-hosts`) and careful timing matter. For an internal audit of your own infrastructure during a maintenance window, blast away with `-T4` and get it done.

Knowing what Nmap can do is half the job. Knowing when to pull back is the other half.
