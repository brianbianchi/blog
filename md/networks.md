# How Networks Work

When data travels from your browser to a web server and back, it passes through a layered system of rules and protocols. Those layers, and the protocols running inside them, are the foundation for everything else in networking and security.

## The OSI Model

The OSI (Open Systems Interconnection) model breaks network communication into 7 layers. Each layer has a specific job and passes data to the layer above or below it.

| Layer | Name | What it does | Examples |
|-------|------|-------------|---------|
| 7 | Application | Interface for user-facing apps | HTTP, DNS, FTP, SMTP |
| 6 | Presentation | Encoding, encryption, compression | TLS, JPEG, ASCII |
| 5 | Session | Opens and manages sessions between hosts | NetBIOS, RPC |
| 4 | Transport | End-to-end delivery, ports, reliability | TCP, UDP |
| 3 | Network | Logical addressing and routing | IP, ICMP, ARP |
| 2 | Data Link | Physical addressing on the local network | Ethernet, MAC addresses |
| 1 | Physical | Raw bits over a medium | Cables, radio waves, fiber |

Most of your time will be spent thinking about layers 3, 4, and 7. A firewall operating at layer 4 makes decisions based on TCP/UDP ports. A WAF operating at layer 7 is inspecting actual HTTP content.

## The TCP/IP Model

The TCP/IP model is a simpler 4-layer version that reflects how the internet actually works:

| TCP/IP Layer | Corresponds to OSI Layers |
|-------------|--------------------------|
| Application | 5, 6, 7 |
| Transport | 4 |
| Internet | 3 |
| Network Access | 1, 2 |

As data travels down the stack it gets **encapsulated**, meaning each layer wraps it with its own header. On the receiving end, each layer strips its header off as data travels back up.

## TCP vs UDP

At the transport layer, two protocols handle delivery of data.

**TCP (Transmission Control Protocol)** is connection-oriented. Before any data is sent, the two hosts complete a **three-way handshake**:

1. **SYN:** the client sends a synchronize packet to initiate a connection
2. **SYN-ACK:** the server acknowledges and responds
3. **ACK:** the client confirms and the connection is established

TCP guarantees delivery, ordering, and error checking. Lost packets get retransmitted. This makes it reliable but adds overhead. HTTP, SSH, FTP, and SMTP all use TCP.

**UDP (User Datagram Protocol)** is connectionless. Packets are sent with no handshake and no guarantee of delivery or order. That makes it fast but unreliable, which is fine for DNS, DHCP, video streaming, VoIP, and gaming, where speed matters more than perfection.

## IP Addressing

Every device on a network has an IP address. IPv4 addresses are 32 bits written in dotted decimal notation like `192.168.1.10`.

An IP address has two parts. The **network portion** identifies which network the device is on, and the **host portion** identifies the specific device within it. The **subnet mask** defines the boundary between the two.

### Subnetting

A subnet mask of `255.255.255.0` (written as `/24` in CIDR notation) means the first 24 bits belong to the network and the last 8 bits are available for hosts.

| CIDR | Subnet Mask | Usable Hosts |
|------|-------------|-------------|
| /24 | 255.255.255.0 | 254 |
| /25 | 255.255.255.128 | 126 |
| /26 | 255.255.255.192 | 62 |
| /30 | 255.255.255.252 | 2 |

Two addresses in every subnet are reserved: the **network address** (all host bits set to 0) and the **broadcast address** (all host bits set to 1). Everything between them is usable.

The following ranges are private and not routable on the public internet:

| Range | CIDR |
|-------|------|
| 10.0.0.0 to 10.255.255.255 | 10.0.0.0/8 |
| 172.16.0.0 to 172.31.255.255 | 172.16.0.0/12 |
| 192.168.0.0 to 192.168.255.255 | 192.168.0.0/16 |

If you see one of these addresses, the device is sitting behind NAT.

## ARP

ARP (Address Resolution Protocol) solves a specific problem: you know a device's IP address, but you need its MAC address to actually send it data on the local network.

IP addresses handle routing between networks. MAC addresses handle delivery within a network. When a device wants to reach `192.168.1.5`, it broadcasts a request to everyone on the local network asking who owns that IP. The device with that address responds with its MAC. That pairing gets cached in the ARP table.

You can see your current ARP cache by running:

```
arp -a
```

ARP has no authentication. Any device can send an unsolicited reply claiming to own any IP address. This is the basis of ARP spoofing, where an attacker poisons the ARP caches of nearby hosts to redirect traffic through their machine.

## DNS

DNS (Domain Name System) translates domain names like `example.com` into IP addresses. It works as a hierarchical, distributed database spread across many servers worldwide.

When you type `example.com` into a browser:

1. Your device checks its local DNS cache
2. If nothing is cached, it asks your **recursive resolver** (typically from your ISP or a public option like `8.8.8.8`)
3. The resolver asks a **root nameserver** where `.com` lives
4. The root points to the **TLD nameserver** for `.com`
5. The TLD nameserver points to the **authoritative nameserver** for `example.com`
6. The authoritative server returns the IP address
7. Your device connects to that IP

### Common DNS Record Types

| Record | Purpose |
|--------|---------|
| A | Maps a domain to an IPv4 address |
| AAAA | Maps a domain to an IPv6 address |
| CNAME | Alias from one domain to another |
| MX | Mail server for the domain |
| TXT | Arbitrary text, used for SPF, DKIM, and verification |
| NS | Authoritative nameservers for the domain |
| PTR | Reverse lookup from IP to domain name |

Standard queries use UDP on port 53. Large responses and zone transfers use TCP on port 53.

DNS has no built-in authentication in its base form, which is what makes DNS spoofing and cache poisoning possible. DNSSEC adds cryptographic verification, but real-world adoption is still inconsistent.

## How It All Fits Together

When you visit `https://example.com`:

1. **DNS** resolves `example.com` to an IP address
2. **ARP** resolves the next-hop router's IP to a MAC address
3. A **TCP SYN** packet goes to port 443 on that IP
4. A **TLS handshake** happens at the presentation layer
5. An **HTTP GET** request travels through the encrypted tunnel
6. The server responds and the data works its way back up the stack to your browser

Every one of those steps is a place where something can go wrong, or where an attacker can interfere. Knowing what normal looks like is what makes the abnormal recognizable.
