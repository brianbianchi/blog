# Anatomy of a Web Request

Loading a web page sends a request through many layers of infrastructure, from a client device to a data center and back, typically in under 100 milliseconds. This is a bottom-up map of how that works, starting from raw bits on a wire and moving up through DNS, TLS, and HTTP.

## OSI Model

The OSI model divides network communication into seven layers. Each layer passes data to the one above or below it.

| Layer | Name         | What it does                            | Examples                   |
| ----- | ------------ | --------------------------------------- | -------------------------- |
| 7     | Application  | User-facing app interface               | HTTP, DNS, FTP, SMTP       |
| 6     | Presentation | Encoding, encryption, compression       | TLS, JPEG, ASCII           |
| 5     | Session      | Opens/manages sessions between hosts    | NetBIOS, RPC               |
| 4     | Transport    | End-to-end delivery, ports, reliability | TCP, UDP                   |
| 3     | Network      | Logical addressing and routing          | IP, ICMP, ARP              |
| 2     | Data Link    | Physical addressing on local network    | Ethernet, MAC addresses    |
| 1     | Physical     | Raw bits over a medium                  | Cables, radio waves, fiber |

Layers 3, 4, and 7 matter most in practice. Layer-4 firewalls filter on ports. Layer-7 WAFs inspect HTTP content.

## TCP/IP Model

| TCP/IP Layer   | OSI Layers |
| -------------- | ---------- |
| Application    | 5, 6, 7    |
| Transport      | 4          |
| Internet       | 3          |
| Network Access | 1, 2       |

Data moving down the stack is **encapsulated** with a header. Moving back up the stack, each layer strips its own header off.

## TCP vs UDP

**TCP** is connection-oriented and begins with a three-way handshake before data flows:

1. **SYN** - the client initiates the connection.
2. **SYN-ACK** - the server acknowledges.
3. **ACK** - the client confirms, and the connection is established.

TCP guarantees delivery, ordering, and error checking. Lost packets are retransmitted. It is used by HTTP, SSH, FTP, and SMTP.

**UDP** is connectionless. It has no handshake, no delivery guarantee, and no ordering, which makes it fast. It is used by DNS, DHCP, streaming, VoIP, and gaming.

### Congestion Control

TCP does not assume the network is reliable. The sender maintains a **congestion window**, a limit on unacknowledged bytes in flight.

- **Slow start** - the window doubles per acknowledged packet until a threshold is reached.
- **Congestion avoidance**, after the threshold, the window grows linearly.
- **On packet loss**, the window shrinks, and the sender backs off and retransmits.

Modern Linux systems use **CUBIC**; older systems use **New Reno**.

## IP Addressing

IPv4 addresses are 32 bits, written in dotted decimal notation (`192.168.1.10`), and consist of two parts:

- **Network portion** - identifies the network.
- **Host portion** - identifies the device on that network.

The **subnet mask** defines the boundary between the two.

### Subnetting

`/24` (255.255.255.0) reserves 24 bits for the network and 8 bits for hosts.

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

Network Address Translation lets multiple devices share one public IP. The router maintains a translation table mapping internal `ip:port` pairs to the external address. Outbound traffic receives the public IP; responses are translated back.

## DHCP

DHCP automatically assigns IP addresses to devices, using UDP ports 67 (server) and 68 (client).

DORA process:

1. **Discover** - the client broadcasts a request for a server.
2. **Offer** - the server offers an IP lease.
3. **Request** - the client requests the offered IP.
4. **Acknowledge** - the server confirms the lease.

## ARP

ARP resolves an IP address to a MAC address on the local network.

When a device needs to reach `192.168.1.5`, it broadcasts a request asking which device owns that IP. The owner responds with its MAC address, and the pairing is cached in the ARP table.

```
arp -a
```

ARP includes no authentication, so any device can claim any IP. This enables **ARP spoofing**, where an attacker poisons nearby ARP caches to intercept traffic.

## ICMP

ICMP handles error reporting and diagnostics at the network layer and is not used for data transfer.

- `ping` - sends ICMP Echo Requests to measure reachability and round-trip time.
- `traceroute` - increments the TTL to map each hop to a destination.

ICMP is often rate-limited or blocked at firewalls.

## DNS

DNS (Domain Name System) maps human-readable domain names to IP addresses. It is a hierarchical, distributed database, and no single server holds all the answers.

### Who Controls the Namespace

- **ICANN** - a non-profit that coordinates the global DNS namespace, contracts with registries, accredits registrars, and manages the root zone.
- **Registries** - one per TLD, operate the authoritative nameservers for that TLD and maintain the zone file. Verisign runs `.com`, with more than 130 million domains.
- **Registrars** - the retail layer (GoDaddy, Namecheap, Cloudflare). They sell domains to end users and report registrations to the registry.
- **Root Zone File** - managed by ICANN and served by root nameservers, it maps every TLD to its registry's nameservers.

Registering `example.com` involves the registrar notifying Verisign, which adds an NS record to the `.com` zone, making the domain resolvable.

### The Hierarchy

```
Root (.)
└── TLD (.com, .org, .io)
    └── Domain (google.com)
        └── Subdomain (mail.google.com)
```

- **Root nameservers** - 13 logical servers, labeled A through M, distributed globally via anycast. They know where every TLD's nameservers are located.
- **TLD nameservers** - operated by registries, such as Verisign for `.com`. They know which nameservers are authoritative for each domain.
- **Authoritative nameservers** - hold the actual DNS records for a domain and provide the final answer.

### Resolution

Resolving `mail.google.com` proceeds as follows:

1. Check the **local cache** (browser, OS stub resolver).
2. Ask the **recursive resolver**, usually an ISP resolver or a public one like `8.8.8.8`.
3. The recursive resolver checks its own cache.
4. If not cached, it queries a **root nameserver** and receives the `.com` TLD nameservers.
5. It queries the `.com` TLD and receives Google's authoritative nameservers.
6. It queries Google's nameserver and receives the IP for `mail.google.com`.
7. The resolver caches the result and returns it.

**Recursive** resolvers perform the lookup on behalf of the client. **Authoritative** servers answer with the actual records and do not forward requests.

Google returns multiple A records (IPv4) and AAAA records (IPv6). Browsers often race both in parallel using **Happy Eyeballs**, connecting through whichever responds first.

### TTL and Caching

Every DNS record has a TTL (Time to Live) in seconds. Resolvers cache results until the TTL expires, then re-query. A lower TTL before a migration allows faster propagation; a higher TTL reduces load on nameservers.

### Record Types

| Record | Purpose                                                            |
| ------ | ------------------------------------------------------------------ |
| A      | Domain → IPv4 address                                              |
| AAAA   | Domain → IPv6 address                                              |
| CNAME  | Alias from one name to another                                     |
| MX     | Mail server for the domain (with priority)                         |
| TXT    | Arbitrary text - SPF, DKIM, domain verification                    |
| NS     | Authoritative nameservers for the domain                           |
| PTR    | Reverse lookup - IP → domain name                                  |
| SOA    | Zone metadata - primary NS, admin email, serial, refresh intervals |
| SRV    | Service location - host, port, priority, weight                    |
| CAA    | Which CAs are allowed to issue certs for the domain                |

### UDP vs TCP

Standard queries use **UDP port 53**, which is fast and low overhead. TCP port 53 is used for:

- Responses larger than 512 bytes (common with DNSSEC)
- Zone transfers (AXFR) between nameservers

### DNSSEC

DNSSEC adds cryptographic signatures to DNS records so resolvers can verify that a record actually came from the legitimate zone owner.

- **RRSIG** - a signature over a record set.
- **DNSKEY** - the public key for the zone.
- **DS** - a hash of a child zone's key, stored in the parent zone.

DNSSEC prevents cache poisoning but does not encrypt queries; that function belongs to DNS over HTTPS or TLS.

### DNS over HTTPS / TLS

Standard DNS is transmitted in plaintext, so anyone on the path, such as an ISP or router, can see every domain being queried.

- **DoH (DNS over HTTPS)** - queries are sent as HTTPS on port 443, blending in with normal web traffic.
- **DoT (DNS over TLS)** - encrypted DNS on port 853, which is easier to identify and block.

Both encrypt the query itself; the destination IP address remains visible.

### Common Attacks

**Cache poisoning** - injecting a forged record into a resolver's cache so victims are directed to an attacker-controlled IP. DNSSEC prevents this; randomized source ports and bailiwick rules reduce exposure.

**DNS hijacking** - compromising a registrar account or nameserver to change authoritative records. Registry locks and two-factor authentication on registrar accounts help prevent this.

**DNS amplification** - sending spoofed queries using the victim's IP as the source. The resolver sends large responses to the victim, a technique used in DDoS attacks.

**DNS tunneling** - encoding data inside DNS queries and responses to exfiltrate data or tunnel command-and-control traffic through firewalls that permit DNS.

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

1. **ClientHello** - the browser sends supported TLS versions, cipher suites, and a random value.
2. **ServerHello** - the server selects a cipher suite and sends its certificate and a random value.
3. **Certificate verification** - the browser validates the certificate against trusted CAs, checks expiry, and confirms the hostname matches.
4. **Key exchange** - the browser and server derive a shared session key, typically via ECDHE in modern TLS.
5. **Finished** - both sides confirm the handshake, and encrypted communication begins.

TLS 1.3 completes this exchange in one round trip; TLS 1.2 requires two.

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

HTTP/2 multiplexes multiple requests over a single TCP connection. HTTP/3 runs over QUIC (UDP), eliminating TCP head-of-line blocking entirely.

If the browser has a cached copy and previously received an `ETag`, it sends an `If-None-Match` header. The server responds with `304 Not Modified` and no body, and the browser serves the cached version.

The server's response includes headers such as `Strict-Transport-Security` (HSTS), which instructs the browser to enforce HTTPS-only connections for future visits without waiting for a redirect.

## Request Flow

Visiting `https://example.com` proceeds as follows:

1. **DNS** resolves `example.com` to an IP address.
2. **ARP** resolves the next-hop router's IP to a MAC address.
3. A **TCP SYN** is sent to port 443.
4. The **TLS handshake** completes. The certificate is verified and a session key is derived.
5. An **HTTP GET** request is sent through the encrypted tunnel.
6. The response travels back up the stack to the browser.

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
