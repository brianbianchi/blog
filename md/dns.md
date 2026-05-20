# DNS

DNS (Domain Name System) maps human-readable domain names to IP addresses. It's a hierarchical, distributed database — no single server holds all the answers.

## Who Controls the Namespace

- **ICANN** — non-profit that coordinates the global DNS namespace. Contracts with registries, accredits registrars, and manages the root zone.
- **Registries** — one per TLD, operate the authoritative nameservers for that TLD and maintain the zone file. Verisign runs `.com` (130M+ domains, $1B+ ARR).
- **Registrars** — retail layer (GoDaddy, Namecheap, Cloudflare). Sell domains to end users and report registrations to the registry.
- **Root Zone File** — a distributed file, managed by ICANN and served by root nameservers, that maps every TLD to its registry's nameservers. It's what makes the hierarchy work.

When you register `example.com`: registrar → notifies Verisign → Verisign adds an NS record to the `.com` zone → root zone delegates `.com` to Verisign → your domain becomes resolvable.

## The Hierarchy

```
Root (.)
└── TLD (.com, .org, .io)
    └── Domain (google.com)
        └── Subdomain (mail.google.com)
```

- **Root nameservers** — 13 logical servers (labeled A–M), distributed globally via anycast. They know where every TLD's nameservers live.
- **TLD nameservers** — operated by registries (Verisign for `.com`). They know which nameservers are authoritative for each domain.
- **Authoritative nameservers** — hold the actual DNS records for a domain. The final word.

## Resolution

When you query `mail.google.com`:

1. Check **local cache** (browser, OS stub resolver)
2. Ask the **recursive resolver** — usually your ISP or a public resolver like `8.8.8.8`
3. Recursive resolver checks its cache
4. If not cached, it queries a **root nameserver** → gets `.com` TLD nameservers
5. Queries `.com` TLD → gets Google's authoritative nameservers
6. Queries Google's nameserver → gets the IP for `mail.google.com`
7. Resolver caches the result and returns it

**Recursive** resolvers do the legwork on your behalf. **Authoritative** servers answer with actual records — no forwarding.

## TTL and Caching

Every DNS record has a TTL (Time to Live) in seconds. Resolvers cache results until TTL expires, then re-query. Lower TTL before a migration for faster propagation; higher TTL reduces load on nameservers.

## Record Types

| Record | Purpose |
|--------|---------|
| A | Domain → IPv4 address |
| AAAA | Domain → IPv6 address |
| CNAME | Alias from one name to another |
| MX | Mail server for the domain (with priority) |
| TXT | Arbitrary text — SPF, DKIM, domain verification |
| NS | Authoritative nameservers for the domain |
| PTR | Reverse lookup: IP → domain name |
| SOA | Zone metadata — primary NS, admin email, serial, refresh intervals |
| SRV | Service location — host, port, priority, weight |
| CAA | Which CAs are allowed to issue certs for the domain |

## UDP vs TCP

Standard queries use **UDP port 53** — fast, low overhead. TCP port 53 is used for:
- Responses larger than 512 bytes (common with DNSSEC)
- Zone transfers (AXFR) between nameservers

## DNSSEC

Adds cryptographic signatures to DNS records so resolvers can verify a record actually came from the legitimate zone owner.

- **RRSIG** — signature over a record set
- **DNSKEY** — public key for the zone
- **DS** — hash of a child zone's key, stored in the parent zone

Prevents cache poisoning but doesn't encrypt queries — that's DNS over HTTPS/TLS.

## DNS over HTTPS / TLS

Standard DNS is plaintext. Anyone on the path (ISP, router) can see every domain you query.

- **DoH (DNS over HTTPS)** — queries sent as HTTPS to port 443, blends in with normal web traffic
- **DoT (DNS over TLS)** — encrypted DNS on port 853, easier to identify and block

Both encrypt the query. The destination IP is still visible.

## Common Attacks

**Cache poisoning** — inject a forged record into a resolver's cache so victims get directed to an attacker-controlled IP. DNSSEC prevents it; randomized source ports and bailiwick rules reduce exposure.

**DNS hijacking** — compromise a registrar account or nameserver to change authoritative records. Registry locks and 2FA on registrar accounts help.

**DNS amplification** — send spoofed queries with the victim's IP as source. Resolver sends large responses to the victim. Used in DDoS.

**DNS tunneling** — encode data inside DNS queries and responses to exfiltrate data or tunnel C2 traffic through firewalls that allow DNS.

## Tools

```bash
dig google.com              # basic A record lookup
dig google.com MX           # query specific record type
dig @8.8.8.8 google.com     # query a specific resolver
dig +trace google.com       # follow the full resolution chain
dig -x 8.8.8.8              # reverse lookup (PTR)
nslookup google.com         # simpler alternative to dig
whois google.com            # registrar and registration info
```
