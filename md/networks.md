# Anatomy of a Web Request

Loading a web page is like mailing a letter and getting a reply, except the round trip usually takes less than a second. The browser finds the address, opens a private line to the server, asks for the page, and displays the answer.

## Layers

Networks split the work into layers, much like a postal service. One person writes the letter, another puts it in an envelope, another sorts it, and a truck carries it. Each only needs to do its own job.

| Layer       | Job                                  | Examples            |
| ----------- | ------------------------------------ | ------------------- |
| Application | What the app wants to say            | HTTP, DNS           |
| Transport   | Delivers data to the right program   | TCP, UDP            |
| Internet    | Finds a route between networks       | IP                  |
| Link        | Moves data across the physical wire  | Ethernet, Wi-Fi     |

Data is wrapped in another envelope at each layer on the way out. Each layer removes its own envelope on the way in.

This four-layer version is the **TCP/IP model**. The **OSI model** describes the same idea with seven layers.

## TCP and UDP

**TCP** is like a phone call. Both sides first confirm that they can hear each other, using a three-step greeting:

1. **SYN** - "Can you hear me?"
2. **SYN-ACK** - "Yes. Can you hear me?"
3. **ACK** - "Yes."

TCP then makes sure everything arrives, in order. Anything lost is sent again. If the network looks busy, TCP slows down.

**UDP** is like dropping postcards in a mailbox. There is no greeting and no guarantee of arrival, which makes it fast. Video calls and games use it because fresh data matters more than perfect data.

## IP Addresses

Every device on a network has an **IP address**, such as `192.168.1.10`. Like a street address, part of it names the neighborhood (the network) and the rest names the house (the device).

Home networks use private addresses that only work inside the home. **NAT** lets every device in the home share one public address. The router remembers who asked for what, so replies reach the right device, much like a front desk sorting mail for an office building.

## Joining a Network

Two small helpers run when a device joins a network:

- **DHCP** hands the device an IP address, like a hotel assigning a room.
- **ARP** finds the physical hardware address (MAC address) that goes with an IP address nearby. The device asks the room, "Who has this address?" and the owner answers. Nothing checks that the answer is true, so an attacker on the same network can lie.

## ICMP

ICMP is how networks report problems. It carries no web traffic, but two common tools rely on it:

- `ping` checks whether a device is reachable and how long a reply takes.
- `traceroute` lists each stop along the path to a destination.

## DNS

Computers connect using IP addresses, but people remember names. DNS is the internet's phone book, turning `google.com` into an IP address.

No single server holds the whole book. It is split into levels, each knowing who to ask next:

```
Root (.)
└── TLD (.com, .org, .io)
    └── Domain (google.com)
        └── Subdomain (mail.google.com)
```

### Looking Up a Name

Looking up `mail.google.com` works like asking for directions:

1. The computer checks whether it already knows the answer.
2. If not, it asks a **resolver**, a helper usually run by the internet provider.
3. The resolver asks a **root server**, which points to the `.com` servers.
4. The `.com` servers point to Google's servers.
5. Google's servers give the final answer.
6. The resolver returns the answer and remembers it for next time.

Each answer comes with a **TTL**, the number of seconds it may be remembered before someone has to ask again.

### Who Runs It

- **ICANN** oversees the system as a whole.
- **Registries** run each ending. Verisign runs `.com`.
- **Registrars** are the shops that sell domain names, such as Namecheap and Cloudflare.

### Common Records

| Record | Purpose                                 |
| ------ | --------------------------------------- |
| A      | Name → IPv4 address                     |
| AAAA   | Name → IPv6 address                     |
| CNAME  | One name is an alias for another        |
| MX     | Where to deliver email                  |
| TXT    | Notes, often used to prove ownership    |
| NS     | Which servers hold the domain's records |

### Keeping DNS Safe

Normal DNS is sent in the open, like a postcard. Two additions help:

- **DNSSEC** adds a signature, proving an answer is genuine.
- **DNS over HTTPS** and **DNS over TLS** seal the question in an envelope so others cannot read it.

Common attacks follow from how the system works. **Cache poisoning** slips a fake answer into a resolver's memory. **Hijacking** takes over a domain's account and changes its records.

To try a lookup:

```bash
dig google.com
```

## TLS

TLS is the "S" in HTTPS. It lets a browser and a server talk privately, even across a network neither of them trusts.

1. The browser says hello and lists the encryption methods it supports.
2. The server picks one and shows its **certificate**, an ID card signed by a trusted authority.
3. The browser checks that the ID is valid and matches the site.
4. Both sides create a shared secret key without ever sending the key itself.
5. Everything after that is encrypted.

## HTTP

HTTP is the language of the request itself. Over the private connection, the browser asks for the page:

```
GET / HTTP/2
Host: www.google.com
Accept: text/html
```

The server replies with the page and a status code, such as `200` for success or `404` for not found.

If the browser already has a saved copy, it can ask whether the page has changed. If not, the server answers `304 Not Modified` and the browser reuses its copy.

## Putting It Together

Visiting `https://example.com` follows these steps:

1. **DNS** turns the name into an IP address.
2. **ARP** finds the router on the local network.
3. **TCP** opens a connection to the server.
4. **TLS** makes the connection private.
5. **HTTP** requests the page.
6. The server responds and the browser displays the page.

A rough timeline:

| Time    | What happens              |
| ------- | ------------------------- |
| 0ms     | Enter pressed             |
| ~5ms    | Address found             |
| ~15ms   | Connection opened         |
| ~25ms   | Connection made private   |
| ~30ms   | Request sent              |
| ~70ms   | First data received       |
| ~100ms+ | Page appears              |
