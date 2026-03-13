# Server-Side Request Forgery (SSRF)

Server-Side Request Forgery is a vulnerability where you trick a server into making an HTTP request on your behalf. You don't make the request directly. The server does, from inside the network, to a destination you specify. That's the core of why it's dangerous: the server has access to things you don't.

SSRF used to be a relatively niche finding. Then cloud computing made it critical. The ability to reach internal metadata endpoints from a compromised web application is now one of the most direct paths to cloud credential theft, and from there, to full account compromise.

## The Basic Setup

An application fetches a remote resource based on user-supplied input. Common scenarios:

- An image preview feature that takes a URL and fetches the image server-side
- A webhook configuration where a user specifies a URL to receive notifications
- An import tool that fetches data from a remote URL
- A PDF generator that loads a URL and renders it
- An API that proxies requests to an address the client provides

The intended use is fetching external resources. The vulnerability arises when the server also happily fetches internal resources, using its own network access rather than yours.

```
POST /api/fetch-preview
{"url": "https://legitimate-site.com/image.png"}
```

Change that URL:

```
POST /api/fetch-preview
{"url": "http://192.168.1.1/admin"}
```

If the server fetches it and returns the response, or even if the response time varies predictably, you have SSRF.

## What Attackers Target

**Internal services**: Production networks routinely contain services that are intentionally not exposed to the internet. Internal admin panels, database management interfaces, monitoring tools, internal APIs, Elasticsearch clusters with no authentication because they were "never exposed externally." SSRF gives an attacker a foothold inside the network perimeter without any direct access.

**Cloud metadata endpoints**: This is the high-value target in cloud environments. Every major cloud provider exposes a metadata API at a link-local address that's accessible from within the instance but not from outside.

AWS uses `http://169.254.169.254`. The endpoint at:

```
http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

Lists the IAM roles attached to the instance. A request to:

```
http://169.254.169.254/latest/meta-data/iam/security-credentials/<role-name>
```

Returns temporary AWS credentials: an `AccessKeyId`, `SecretAccessKey`, and `SessionToken`. Those credentials can be used immediately from anywhere with an internet connection to call AWS APIs with whatever permissions that role has. If the role has broad permissions (which instance roles often do), this is full cloud account compromise from a single SSRF.

GCP's metadata endpoint is `http://metadata.google.internal/computeMetadata/v1/` (requires a `Metadata-Flavor: Google` header). Azure's is `http://169.254.169.254/metadata/instance` (requires `Metadata: true`). The header requirements are a mild inconvenience, not a meaningful security control, since the attacker controls the server making the request.

AWS has partially addressed this with IMDSv2, which requires a token-based flow. Applications running on EC2 should enforce IMDSv2 (set `HttpTokens: required` at the instance level), which makes SSRF-based credential theft harder, though not impossible if the application can be made to perform the two-step request sequence.

## Blind SSRF

In many cases, the server makes the request but doesn't return the response body to you. You can't read the internal service's output. This is blind SSRF, and it's still exploitable.

**Time-based inference**: If the request to a port that's open responds quickly but a closed port times out, you can port-scan the internal network by measuring response times. Slow response means the connection was refused or dropped; fast response suggests something is listening.

**Out-of-band callbacks**: Tools like Burp Collaborator (or interactsh, or a self-hosted server) give you a domain that logs all incoming DNS lookups and HTTP requests. Point the SSRF at your Collaborator URL. If you see a DNS lookup or HTTP request arrive, the server is making outbound connections. This confirms SSRF even when you get no useful data back through the application.

From there, you can try to extract data via DNS: if you can get the server to include data in a subdomain lookup (some SSRF contexts allow this), the data appears in your Collaborator DNS logs.

## Port Scanning via SSRF

With a working SSRF and some patience, you can map the internal network:

1. Enumerate common RFC 1918 ranges: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
2. For each IP, try common internal ports: 22 (SSH), 3306 (MySQL), 5432 (Postgres), 6379 (Redis), 9200 (Elasticsearch), 8080, 8443, admin ports

The time differences between "connection refused" and "connection accepted" or "connection timed out" let you build a picture of the internal topology. Redis in particular is dangerous here: it speaks a text protocol and sometimes allows unauthenticated writes, so SSRF to Redis can lead to further exploitation.

## Filter Bypasses

Applications sometimes try to block SSRF with a denylist of internal addresses. These filters are regularly bypassed.

**Localhost aliases**: `127.0.0.1`, `localhost`, `0.0.0.0`, `[::1]`, `::1`. Many filters check for `127.0.0.1` but miss the others.

**Alternative IP encodings**: The IP `127.0.0.1` can be represented as:
- Decimal: `2130706433`
- Octal: `0177.0.0.1`
- Hex: `0x7f000001`
- Mixed: `127.1` (shorthand notation)

```
http://2130706433/
http://0177.0.0.1/
http://0x7f000001/
```

**URL scheme variations**: `http://127.0.0.1` vs `http://127.0.0.1:80` vs `http://127.0.0.1:22` (trying other protocols).

**DNS rebinding**: Register a domain you control that initially resolves to a legitimate external IP. Pass the SSRF validation check. Then, before the server makes the actual request, switch the DNS record to resolve to `127.0.0.1`. The server cached nothing and resolves fresh. This works because DNS TTLs can be set very low (1 second), and some SSRF filters check DNS resolution at validation time rather than at request time.

**Open redirects**: If the SSRF filter validates the URL but follows redirects, an open redirect on an allowlisted domain can be used to redirect the server to an internal address.

```
https://trusted.com/redirect?url=http://169.254.169.254/
```

**URL parsing inconsistencies**: Differences between how the validation code parses a URL and how the HTTP library parses it. A URL like `http://attacker.com@192.168.1.1/` might be validated as pointing to `attacker.com` but the HTTP library uses `192.168.1.1` as the actual host.

## Prevention

### Allowlist, Not Denylist

This is the most important point. Denylists (blocking 127.0.0.1, 169.254.169.254, and RFC 1918 ranges) can be bypassed too easily. An allowlist defines the specific domains or IP ranges the application needs to reach, and blocks everything else.

If the feature is supposed to fetch images from user-uploaded URLs, and those images come from a known CDN or a limited set of domains, allowlist those specific domains. If the business case requires fetching from arbitrary external URLs, that's a harder problem, but at minimum resolve the destination IP and verify it doesn't fall within private address ranges before making the request.

### Disable Redirects

HTTP client libraries follow redirects by default. Disable this, or at minimum re-validate the destination after each redirect. An allowlist check on the initial URL is worthless if the server then follows a redirect to an internal address.

### Don't Return Raw Responses

If the server fetches a URL and returns the raw response body to the user, an attacker can directly read internal service responses. Where possible, process and transform the response rather than proxying it wholesale. A thumbnail generator should return a resized image, not the raw bytes from the fetched URL.

### Egress Proxy

Route all outbound HTTP requests from the application through a dedicated egress proxy. The proxy enforces the allowlist centrally. This is operationally cleaner than implementing per-application allowlisting, and it gives you a single point to monitor and log all outbound requests from your infrastructure.

### Enforce IMDSv2 on Cloud Instances

If you're running on AWS EC2, require IMDSv2 at the instance level. This doesn't eliminate SSRF, but it significantly raises the bar for credential theft via the metadata endpoint.

```bash
aws ec2 modify-instance-metadata-options \
  --instance-id i-xxxx \
  --http-tokens required \
  --http-endpoint enabled
```
