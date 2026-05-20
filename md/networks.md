# Networks

## OSI Model

7 layers. Each passes data to the one above or below.

| Layer | Name | What it does | Examples |
|-------|------|-------------|---------|
| 7 | Application | User-facing app interface | HTTP, DNS, FTP, SMTP |
| 6 | Presentation | Encoding, encryption, compression | TLS, JPEG, ASCII |
| 5 | Session | Opens/manages sessions between hosts | NetBIOS, RPC |
| 4 | Transport | End-to-end delivery, ports, reliability | TCP, UDP |
| 3 | Network | Logical addressing and routing | IP, ICMP, ARP |
| 2 | Data Link | Physical addressing on local network | Ethernet, MAC addresses |
| 1 | Physical | Raw bits over a medium | Cables, radio waves, fiber |

Layers 3, 4, and 7 matter most. Layer-4 firewalls filter on ports. Layer-7 WAFs inspect HTTP content.

## TCP/IP Model

| TCP/IP Layer | OSI Layers |
|-------------|-----------|
| Application | 5, 6, 7 |
| Transport | 4 |
| Internet | 3 |
| Network Access | 1, 2 |

Data going down the stack gets **encapsulated** — each layer wraps it with a header. Going back up, each layer strips its header off.

## TCP vs UDP

**TCP** — connection-oriented. Three-way handshake before data flows:
1. **SYN** — client initiates
2. **SYN-ACK** — server acknowledges
3. **ACK** — client confirms, connection established

Guarantees delivery, ordering, and error checking. Lost packets retransmit. Used by HTTP, SSH, FTP, SMTP.

**UDP** — connectionless. No handshake, no delivery guarantee, no ordering. Fast. Used by DNS, DHCP, streaming, VoIP, gaming.

## IP Addressing

IPv4: 32-bit addresses in dotted decimal (`192.168.1.10`). Two parts:
- **Network portion** — which network
- **Host portion** — which device on that network

The **subnet mask** defines the boundary.

### Subnetting

`/24` (255.255.255.0) = 24 bits for network, 8 bits for hosts.

| CIDR | Subnet Mask | Usable Hosts |
|------|-------------|-------------|
| /24 | 255.255.255.0 | 254 |
| /25 | 255.255.255.128 | 126 |
| /26 | 255.255.255.192 | 62 |
| /30 | 255.255.255.252 | 2 |

Each subnet reserves the network address (all host bits 0) and broadcast address (all host bits 1).

Private ranges (not routable on the public internet):

| Range | CIDR |
|-------|------|
| 10.0.0.0 – 10.255.255.255 | 10.0.0.0/8 |
| 172.16.0.0 – 172.31.255.255 | 172.16.0.0/12 |
| 192.168.0.0 – 192.168.255.255 | 192.168.0.0/16 |

### NAT

Network Address Translation lets multiple devices share one public IP. The router maintains a translation table mapping internal `ip:port` pairs to the external address. Outbound traffic gets the public IP; responses get translated back.

## DHCP

Automatically assigns IP addresses to devices. Uses UDP ports 67 (server) and 68 (client).

DORA process:
1. **Discover** — client broadcasts looking for a server
2. **Offer** — server offers an IP lease
3. **Request** — client requests the offered IP
4. **Acknowledge** — server confirms the lease

## ARP

Resolves an IP address to a MAC address on the local network.

Device wants to reach `192.168.1.5` → broadcasts asking who owns that IP → owner responds with its MAC → pairing gets cached in the ARP table.

```
arp -a
```

No authentication — any device can claim any IP. This enables **ARP spoofing**, where an attacker poisons nearby ARP caches to intercept traffic.

## ICMP

Handles error reporting and diagnostics at the network layer. Not used for data transfer.

- `ping` — ICMP Echo Requests, measures reachability and RTT
- `traceroute` — increments TTL to map each hop to a destination

Often rate-limited or blocked at firewalls.

## DNS

Translates domain names to IP addresses. Hierarchical and distributed.

Resolution for `example.com`:
1. Check local cache
2. Query **recursive resolver** (ISP or public: `8.8.8.8`, `1.1.1.1`)
3. Resolver asks a **root nameserver** where `.com` lives
4. Root points to the **TLD nameserver** for `.com`
5. TLD points to the **authoritative nameserver** for `example.com`
6. Authoritative server returns the IP

### Record Types

| Record | Purpose |
|--------|---------|
| A | Domain → IPv4 address |
| AAAA | Domain → IPv6 address |
| CNAME | Alias from one domain to another |
| MX | Mail server for the domain |
| TXT | Arbitrary text — SPF, DKIM, verification |
| NS | Authoritative nameservers for the domain |
| PTR | Reverse lookup: IP → domain name |
| SOA | Start of Authority — primary nameserver, zone serial, TTLs |

Standard queries: UDP port 53. Large responses and zone transfers: TCP port 53.

No built-in authentication → DNS spoofing and cache poisoning are possible. DNSSEC adds cryptographic verification but adoption is inconsistent.

## Request Flow

Visiting `https://example.com`:

1. **DNS** resolves `example.com` to an IP
2. **ARP** resolves the next-hop router's IP to a MAC
3. **TCP SYN** to port 443
4. **TLS handshake** at the presentation layer
5. **HTTP GET** through the encrypted tunnel
6. Response travels back up the stack to the browser
