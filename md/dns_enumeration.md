# DNS Enumeration

DNS is one of the richest sources of information about a target organization, and it's almost entirely public by design. The whole point of DNS is to answer questions about your infrastructure. An attacker's goal during enumeration is to ask as many of those questions as possible before ever touching a single server.

What you can learn from DNS alone: IP addresses for all public hosts, mail server configurations, name server providers (which tells you the DNS hosting provider), verification records that hint at which SaaS tools the company uses, and sometimes internal hostnames that were accidentally made resolvable from the internet. That last one happens more than you'd expect.

## Basic Queries with dig and nslookup

`dig` is the tool you want for serious DNS querying. `nslookup` works too and is available on Windows by default, but `dig` gives cleaner output and more control.

The basic syntax for `dig`:

```
dig [record type] [domain] [@nameserver]
```

### Record Types

| Record | Purpose |
|--------|---------|
| A | IPv4 address for a hostname |
| AAAA | IPv6 address |
| CNAME | Alias pointing to another hostname |
| MX | Mail servers for the domain |
| NS | Authoritative nameservers |
| TXT | Arbitrary text; used for SPF, DKIM, DMARC, and domain verification |
| PTR | Reverse lookup; maps an IP to a hostname |
| SOA | Start of Authority; metadata about the zone including admin contact |

Some useful examples:

```
# A record
dig A example.com

# MX records
dig MX example.com

# NS records
dig NS example.com

# TXT records (often very revealing)
dig TXT example.com

# Query a specific nameserver directly
dig A example.com @8.8.8.8
```

With `nslookup`:

```
nslookup -type=MX example.com
nslookup -type=TXT example.com
```

The `host` command is another lightweight option:

```
host -t mx example.com
host -t ns example.com
```

## Zone Transfers (AXFR)

A zone transfer is a mechanism for replicating DNS records from a primary nameserver to a secondary one. The protocol is called AXFR. When it works as intended, only authorized secondary nameservers can request a full copy of a DNS zone.

When it's misconfigured, anyone can ask for the entire zone and get every DNS record back in one response: every hostname, every IP, every subzone delegation. It's essentially a complete inventory of the organization's DNS namespace.

Attempting a zone transfer:

```
dig axfr example.com @ns1.example.com
```

Replace `ns1.example.com` with one of the nameservers returned by your NS query. If the server is misconfigured, you'll get a dump of every record in the zone. If it's properly configured (which most are these days), you'll get a "REFUSED" or "SERVFAIL".

Zone transfers are largely a relic of misconfigured older deployments, but they still exist. Internal DNS servers are especially worth trying, and during an internal penetration test you can sometimes find Windows DNS servers accepting AXFR from any client on the network.

## Subdomain Enumeration

Even when zone transfers fail, you can still discover subdomains by brute-forcing them: systematically trying common names and checking whether they resolve.

The premise is simple. If `example.com` is the target, what about `dev.example.com`, `staging.example.com`, `vpn.example.com`, `jira.example.com`? These subdomains often host internal tools, development environments, and administrative interfaces that were never meant to be public-facing but ended up reachable anyway.

### Brute-Forcing with Wordlists

**gobuster** in DNS mode:

```
gobuster dns -d example.com -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

**amass** is more thorough; it combines brute-forcing with passive sources like certificate transparency logs, threat intelligence feeds, and various DNS datasets:

```
amass enum -d example.com
amass enum -active -d example.com
```

**subfinder** is fast and primarily passive, pulling from APIs and public data sources:

```
subfinder -d example.com
subfinder -d example.com -all -recursive
```

**dnsx** is great for resolving and validating large lists of discovered subdomains:

```
cat subdomains.txt | dnsx -a -resp
```

A common workflow is to run `amass` and `subfinder` for passive discovery, combine the output, then feed everything through `dnsx` to confirm what actually resolves.

### Why Subdomains Matter

Forgotten development and staging environments are notoriously under-patched. A `staging.example.com` might be running a version of the app from six months ago, before a critical vulnerability was fixed. Admin panels that were "only internal" get deployed with public IPs. Test environments get configured with weak credentials and never decommissioned. Subdomains are where old infrastructure goes to be forgotten.

## Reverse DNS Lookups

A forward lookup goes from name to IP. A reverse lookup goes the other direction, from IP to name, using PTR records.

If you have a block of IP addresses associated with an organization (from WHOIS, ARIN, or prior reconnaissance), you can walk through them and see which ones have reverse DNS entries. Those hostnames often reveal what the server does.

```
# Reverse lookup for a single IP
dig -x 93.184.216.34

# Or with host
host 93.184.216.34
```

For sweeping a range, tools like `dnsx` can handle bulk reverse lookups:

```
dnsx -ptr -l ip_list.txt -resp-only
```

PTR records aren't always set, especially for cloud-hosted infrastructure, but when they are, they often contain descriptive names that tell you a lot.

## DNS Cache Snooping

DNS cache snooping is a technique for querying a recursive DNS resolver to infer what domains its clients have recently visited. The idea is that if a resolver has a cached answer for `evil.com`, someone in the network recently resolved that domain.

There are two methods. The non-recursive method sends a query with the recursion desired (RD) flag unset. If the resolver returns an answer from cache, that record was recently looked up. If it returns nothing, the domain probably hasn't been queried recently.

```
dig @target-resolver example.com A +norecurse
```

This has limited offensive value in most scenarios, but it can be useful for threat intelligence work, for understanding what a compromised internal resolver has seen, or for validating whether a domain is in active use.

## What to Look for in Results

Not all DNS records are equally interesting. Here's what to pay attention to:

**MX records** reveal which email provider the organization uses. If their MX points to `mail.protection.outlook.com`, they're on Microsoft 365. If it points to `aspmx.l.google.com`, they're on Google Workspace. This matters for phishing and social engineering assessments.

**TXT records** are particularly revealing. SPF records list the IP addresses and services authorized to send mail on behalf of the domain. A record like `include:salesforce.com include:sendgrid.net include:mailchimp.com` tells you exactly which third-party services are in use. DKIM selectors can expose the email service provider. Domain verification tokens for services like Atlassian or Adobe sometimes linger after decommissioning, hinting at tools the company used.

**NS records** tell you who hosts the DNS. Route53, Cloudflare, Azure DNS, or a self-hosted nameserver each come with different implications for misconfiguration risk.

**CNAME records** sometimes point to external services (like `careers.example.com` pointing to a Greenhouse or Lever URL). If that external service is no longer configured, the subdomain may be vulnerable to subdomain takeover.

**Internal hostnames leaking** is one of the more interesting findings. Split-horizon DNS is supposed to serve different answers to internal vs. external resolvers, but it's commonly misconfigured. Hostnames like `dc01.corp.example.com` or `172.16.1.10` resolving publicly give you a direct window into internal network structure.

## Useful Tools Summary

| Tool | Primary Use |
|------|-------------|
| `dig` | Manual DNS queries, zone transfers |
| `nslookup` | Basic DNS queries, works on Windows |
| `host` | Quick lookups, simple output |
| `fierce` | Subdomain enumeration with zone transfer attempts |
| `amass` | Comprehensive subdomain enumeration using passive and active methods |
| `subfinder` | Fast passive subdomain discovery |
| `dnsx` | Bulk DNS resolution and validation |

DNS enumeration is low-risk, requires no authentication, and produces an enormous amount of useful information. It should be one of the first things done in any external reconnaissance phase.
