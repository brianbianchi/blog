# Networks

Every time you load a page, a request travels through a dozen layers of infrastructure — from your keyboard to a data center and back, in under 100ms. This is a bottom-up map of how it works, from raw bits on a wire all the way up through DNS, TLS, and HTTP.

## OSI Model

7 layers. Each passes data to the one above or below.

| Layer | Name         | What it does                            | Examples                   |
| ----- | ------------ | --------------------------------------- | -------------------------- |
| 7     | Application  | User-facing app interface               | HTTP, DNS, FTP, SMTP       |
| 6     | Presentation | Encoding, encryption, compression       | TLS, JPEG, ASCII           |
| 5     | Session      | Opens/manages sessions between hosts    | NetBIOS, RPC               |
| 4     | Transport    | End-to-end delivery, ports, reliability | TCP, UDP                   |
| 3     | Network      | Logical addressing and routing          | IP, ICMP, ARP              |
| 2     | Data Link    | Physical addressing on local network    | Ethernet, MAC addresses    |
| 1     | Physical     | Raw bits over a medium                  | Cables, radio waves, fiber |

Layers 3, 4, and 7 matter most. Layer-4 firewalls filter on ports. Layer-7 WAFs inspect HTTP content.

## TCP/IP Model

| TCP/IP Layer   | OSI Layers |
| -------------- | ---------- |
| Application    | 5, 6, 7    |
| Transport      | 4          |
| Internet       | 3          |
| Network Access | 1, 2       |

Data going down the stack gets **encapsulated** — each layer wraps it with a header. Going back up, each layer strips its header off.

## TCP vs UDP

**TCP** — connection-oriented. Three-way handshake before data flows:
1. **SYN** — client initiates
2. **SYN-ACK** — server acknowledges
3. **ACK** — client confirms, connection established

Guarantees delivery, ordering, and error checking. Lost packets retransmit. Used by HTTP, SSH, FTP, SMTP.

**UDP** — connectionless. No handshake, no delivery guarantee, no ordering. Fast. Used by DNS, DHCP, streaming, VoIP, gaming.

### Congestion Control

TCP doesn't assume the network is reliable. The sender maintains a **congestion window** — a limit on unacknowledged bytes in flight.

- **Slow start** — window doubles per acknowledged packet until a threshold is hit
- **Congestion avoidance** — after the threshold, window grows linearly
- **On packet loss** — window shrinks; sender backs off and retransmits

Modern Linux uses **CUBIC**; older systems use **New Reno**.

## IP Addressing

IPv4: 32-bit addresses in dotted decimal (`192.168.1.10`). Two parts:
- **Network portion** — which network
- **Host portion** — which device on that network

The **subnet mask** defines the boundary.

### Subnetting

`/24` (255.255.255.0) = 24 bits for network, 8 bits for hosts.

| CIDR | Subnet Mask     | Usable Hosts |
| ---- | --------------- | ------------ |
| /24  | 255.255.255.0   | 254          |
| /25  | 255.255.255.128 | 126          |
| /26  | 255.255.255.192 | 62           |
| /30  | 255.255.255.252 | 2            |

Each subnet reserves the network address (all host bits 0) and broadcast address (all host bits 1).

Private ranges (not routable on the public internet):

| Range                         | CIDR           |
| ----------------------------- | -------------- |
| 10.0.0.0 – 10.255.255.255     | 10.0.0.0/8     |
| 172.16.0.0 – 172.31.255.255   | 172.16.0.0/12  |
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

DNS (Domain Name System) maps human-readable domain names to IP addresses. It's a hierarchical, distributed database. No single server holds all the answers.

### Who Controls the Namespace

- **ICANN** — non-profit that coordinates the global DNS namespace. Contracts with registries, accredits registrars, and manages the root zone.
- **Registries** — one per TLD, operate the authoritative nameservers for that TLD and maintain the zone file. Verisign runs `.com` (130M+ domains).
- **Registrars** — retail layer (GoDaddy, Namecheap, Cloudflare). Sell domains to end users and report registrations to the registry.
- **Root Zone File** — managed by ICANN and served by root nameservers, maps every TLD to its registry's nameservers.

When you register `example.com`: registrar → notifies Verisign → Verisign adds an NS record to the `.com` zone → your domain becomes resolvable.

### The Hierarchy

```
Root (.)
└── TLD (.com, .org, .io)
    └── Domain (google.com)
        └── Subdomain (mail.google.com)
```

- **Root nameservers** — 13 logical servers (labeled A–M), distributed globally via anycast. They know where every TLD's nameservers live.
- **TLD nameservers** — operated by registries (Verisign for `.com`). They know which nameservers are authoritative for each domain.
- **Authoritative nameservers** — hold the actual DNS records for a domain. The final word.

### Resolution

When you query `mail.google.com`:

1. Check **local cache** (browser, OS stub resolver)
2. Ask the **recursive resolver** — usually your ISP or a public resolver like `8.8.8.8`
3. Recursive resolver checks its cache
4. If not cached, it queries a **root nameserver** → gets `.com` TLD nameservers
5. Queries `.com` TLD → gets Google's authoritative nameservers
6. Queries Google's nameserver → gets the IP for `mail.google.com`
7. Resolver caches the result and returns it

**Recursive** resolvers do the legwork on your behalf. **Authoritative** servers answer with actual records — no forwarding.

Google returns multiple A records (IPv4) and AAAA records (IPv6). Browsers often race both in parallel using **Happy Eyeballs**, connecting on whichever responds first.

### TTL and Caching

Every DNS record has a TTL (Time to Live) in seconds. Resolvers cache results until TTL expires, then re-query. Lower TTL before a migration for faster propagation; higher TTL reduces load on nameservers.

### Record Types

| Record | Purpose                                                            |
| ------ | ------------------------------------------------------------------ |
| A      | Domain → IPv4 address                                              |
| AAAA   | Domain → IPv6 address                                              |
| CNAME  | Alias from one name to another                                     |
| MX     | Mail server for the domain (with priority)                         |
| TXT    | Arbitrary text — SPF, DKIM, domain verification                    |
| NS     | Authoritative nameservers for the domain                           |
| PTR    | Reverse lookup: IP → domain name                                   |
| SOA    | Zone metadata — primary NS, admin email, serial, refresh intervals |
| SRV    | Service location — host, port, priority, weight                    |
| CAA    | Which CAs are allowed to issue certs for the domain                |

### UDP vs TCP

Standard queries use **UDP port 53** — fast, low overhead. TCP port 53 is used for:
- Responses larger than 512 bytes (common with DNSSEC)
- Zone transfers (AXFR) between nameservers

### DNSSEC

Adds cryptographic signatures to DNS records so resolvers can verify a record actually came from the legitimate zone owner.

- **RRSIG** — signature over a record set
- **DNSKEY** — public key for the zone
- **DS** — hash of a child zone's key, stored in the parent zone

Prevents cache poisoning but doesn't encrypt queries — that's DNS over HTTPS/TLS.

### DNS over HTTPS / TLS

Standard DNS is plaintext. Anyone on the path (ISP, router) can see every domain you query.

- **DoH (DNS over HTTPS)** — queries sent as HTTPS to port 443, blends in with normal web traffic
- **DoT (DNS over TLS)** — encrypted DNS on port 853, easier to identify and block

Both encrypt the query. The destination IP is still visible.

### Common Attacks

**Cache poisoning** — inject a forged record into a resolver's cache so victims get directed to an attacker-controlled IP. DNSSEC prevents it; randomized source ports and bailiwick rules reduce exposure.

**DNS hijacking** — compromise a registrar account or nameserver to change authoritative records. Registry locks and 2FA on registrar accounts help.

**DNS amplification** — send spoofed queries with the victim's IP as source. Resolver sends large responses to the victim. Used in DDoS.

**DNS tunneling** — encode data inside DNS queries and responses to exfiltrate data or tunnel C2 traffic through firewalls that allow DNS.

### Tools

```bash
dig google.com              # basic A record lookup
dig google.com MX           # query specific record type
dig @8.8.8.8 google.com     # query a specific resolver
dig +trace google.com       # follow the full resolution chain
dig -x 8.8.8.8              # reverse lookup (PTR)
nslookup google.com         # simpler alternative to dig
whois google.com            # registrar and registration info
```

## TLS

HTTPS requires a TLS handshake over the TCP connection:

1. **ClientHello** — browser sends supported TLS versions, cipher suites, and a random value
2. **ServerHello** — server picks a cipher suite, sends its certificate and a random value
3. **Certificate verification** — browser validates the cert against trusted CAs, checks expiry, confirms the hostname matches
4. **Key exchange** — browser and server derive a shared session key (via ECDHE in modern TLS)
5. **Finished** — both sides confirm the handshake; encrypted communication begins

TLS 1.3 completes this in one round trip. TLS 1.2 takes two.

## HTTP

The browser sends a GET request through the encrypted tunnel:

```
GET / HTTP/2
Host: www.google.com
User-Agent: ...
Accept: text/html
Accept-Encoding: gzip, br
Cookie: ...
```

HTTP/2 multiplexes multiple requests over a single TCP connection. HTTP/3 runs over QUIC (UDP) to eliminate TCP head-of-line blocking entirely.

If the browser has a cached copy and received an `ETag` previously, it sends an `If-None-Match` header. The server responds `304 Not Modified` with no body, and the browser serves the cached version.

The server's response includes headers like `Strict-Transport-Security` (HSTS), which tells the browser to enforce HTTPS-only for future visits without waiting for a redirect.

## Request Flow

Visiting `https://example.com`:

1. **DNS** resolves `example.com` to an IP
2. **ARP** resolves the next-hop router's IP to a MAC
3. **TCP SYN** to port 443
4. **TLS handshake** — cert verified, session key derived
5. **HTTP GET** through the encrypted tunnel
6. Response travels back up the stack to the browser

### Timeline

| Step    | What happens                                            |
| ------- | ------------------------------------------------------- |
| 0ms     | Enter pressed                                           |
| ~1ms    | HSTS checked                                            |
| ~5ms    | DNS resolved (cache hit) or ~50–100ms (full resolution) |
| ~6ms    | ARP resolves gateway MAC                                |
| ~15ms   | TCP connection established                              |
| ~25ms   | TLS handshake complete (TLS 1.3)                        |
| ~30ms   | HTTP GET sent                                           |
| ~70ms   | First byte received (TTFB)                              |
| ~100ms+ | Page renders                                            |

