# HTTP

HTTP is the protocol that moves data between clients and servers on the web. Every API call, page load, and image fetch goes over it. The networks post covered the full request flow top to bottom — this goes deeper on HTTP itself.

## Request Structure

```
METHOD /path HTTP/version
Header-Name: value
Another-Header: value

Body (optional)
```

A real GET request:

```
GET /api/users/42 HTTP/2
Host: api.example.com
Authorization: Bearer eyJhbGci...
Accept: application/json
Accept-Encoding: gzip, br
User-Agent: Mozilla/5.0
```

A POST with a body:

```
POST /api/users HTTP/2
Host: api.example.com
Content-Type: application/json
Content-Length: 42

{"name": "Alice", "email": "alice@example.com"}
```

## Response Structure

```
HTTP/version STATUS_CODE Reason Phrase
Header-Name: value

Body
```

```
HTTP/2 200 OK
Content-Type: application/json
Content-Length: 87
Cache-Control: max-age=3600
ETag: "abc123"

{"id": 42, "name": "Alice", "email": "alice@example.com"}
```

## Methods

| Method | Idempotent | Safe | Typical use |
| ------ | ---------- | ---- | ----------- |
| `GET` | Yes | Yes | Retrieve a resource |
| `HEAD` | Yes | Yes | Like GET but no body — check headers, test existence |
| `OPTIONS` | Yes | Yes | What methods does this endpoint support? (also preflight) |
| `POST` | No | No | Create a resource, submit data |
| `PUT` | Yes | No | Replace a resource entirely |
| `PATCH` | No | No | Partial update |
| `DELETE` | Yes | No | Remove a resource |

**Idempotent** means calling it multiple times has the same effect as calling it once. PUT replacing a user with the same data is a no-op on the second call. POST creating a user twice creates two users.

## Status Codes

| Range | Meaning |
| ----- | ------- |
| 1xx | Informational — request received, keep going |
| 2xx | Success |
| 3xx | Redirect |
| 4xx | Client error — you did something wrong |
| 5xx | Server error — the server did something wrong |

The ones you'll actually see:

| Code | Name | When |
| ---- | ---- | ---- |
| 200 | OK | Request succeeded |
| 201 | Created | Resource created (POST/PUT) |
| 204 | No Content | Success, no body (DELETE, PUT) |
| 301 | Moved Permanently | Permanent redirect; browsers and bots update bookmarks |
| 302 | Found | Temporary redirect; don't update bookmarks |
| 304 | Not Modified | Cached version is still valid |
| 307 | Temporary Redirect | Same as 302 but preserves the HTTP method |
| 308 | Permanent Redirect | Same as 301 but preserves the HTTP method |
| 400 | Bad Request | Malformed request, invalid params |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Authenticated but not allowed |
| 404 | Not Found | Resource doesn't exist |
| 405 | Method Not Allowed | That method isn't supported here |
| 409 | Conflict | State conflict — duplicate create, stale update |
| 410 | Gone | Resource permanently deleted |
| 422 | Unprocessable Entity | Valid format, but failed validation |
| 429 | Too Many Requests | Rate limited |
| 500 | Internal Server Error | Something broke server-side |
| 502 | Bad Gateway | Upstream server returned garbage |
| 503 | Service Unavailable | Overloaded or in maintenance |
| 504 | Gateway Timeout | Upstream didn't respond in time |

301 vs 302: browsers follow both, but only cache 301s. 302 vs 307: both are temporary, but 302 allows browsers to change POST to GET on the redirect; 307 doesn't.

## Headers

### Request Headers

| Header | What it does |
| ------ | ------------ |
| `Host` | Target domain — required in HTTP/1.1 |
| `Authorization` | Credentials (`Bearer <token>`, `Basic <base64>`) |
| `Content-Type` | Media type of the request body |
| `Accept` | Media types the client can handle |
| `Accept-Encoding` | Compression formats the client supports (`gzip`, `br`, `zstd`) |
| `Accept-Language` | Preferred language (`en-US, en;q=0.9`) |
| `User-Agent` | Client identifier |
| `Cookie` | Cookies for the domain |
| `Referer` | URL of the page that made this request |
| `Origin` | Origin of the request (for CORS) |
| `If-None-Match` | Send cached ETag — server returns 304 if still valid |
| `If-Modified-Since` | Send cached date — server returns 304 if not changed |

### Response Headers

| Header | What it does |
| ------ | ------------ |
| `Content-Type` | Media type of the response body |
| `Content-Length` | Body size in bytes |
| `Content-Encoding` | Compression applied (`gzip`, `br`) |
| `Location` | URL to redirect to (3xx responses) |
| `Set-Cookie` | Set a cookie |
| `ETag` | Version identifier for the response |
| `Last-Modified` | When the resource last changed |
| `Cache-Control` | Caching directives |
| `Vary` | Which request headers affect the cached response |
| `Strict-Transport-Security` | Force HTTPS for a duration |
| `X-Frame-Options` | Prevent clickjacking (`DENY`, `SAMEORIGIN`) |
| `Content-Security-Policy` | Restrict what resources the page can load |

## Caching

Good caching makes everything faster. `Cache-Control` is how you tell caches what to do.

### Cache-Control Directives

| Directive | Who it applies to | Meaning |
| --------- | ----------------- | ------- |
| `max-age=N` | Browser + CDN | Cache for N seconds |
| `s-maxage=N` | CDN only | CDN cache duration (overrides max-age for CDNs) |
| `no-cache` | Both | Cache it, but always revalidate before using |
| `no-store` | Both | Don't cache at all |
| `private` | Browser only | Don't store in shared caches (CDNs) |
| `public` | Both | Can be stored in any cache |
| `must-revalidate` | Both | Expired cache must revalidate before use |
| `immutable` | Both | Content won't change — skip revalidation |

`no-cache` doesn't mean don't cache — it means always check if the cached version is still fresh. For truly no caching, use `no-store`.

### ETags and Conditional Requests

ETags are fingerprints. Server sends one with the response; browser stores it. Next request, browser sends `If-None-Match: "etag-value"`. If the resource hasn't changed, server returns `304 Not Modified` with no body. Browser uses its cached copy. Saves bandwidth, same end result.

Same idea with `Last-Modified` / `If-Modified-Since` using timestamps instead of hashes.

### Vary

`Vary: Accept-Encoding` tells caches to store separate versions for each encoding. Without it, a CDN might serve a gzip'd response to a client that requested plain text.

## Cookies

Set by the server with `Set-Cookie`, sent by the browser on every matching request.

```
Set-Cookie: session=abc123; Path=/; Domain=example.com; Expires=Fri, 01 Jan 2027 00:00:00 GMT; Secure; HttpOnly; SameSite=Strict
```

| Attribute | What it does |
| --------- | ------------ |
| `Secure` | Only sent over HTTPS |
| `HttpOnly` | Not accessible via JavaScript — protects against XSS token theft |
| `SameSite=Strict` | Only sent on same-site requests — prevents CSRF |
| `SameSite=Lax` | Sent on top-level navigations but not cross-site sub-requests |
| `SameSite=None` | Sent on all requests — requires `Secure` |
| `Domain` | Which domains receive the cookie |
| `Path` | Which paths receive the cookie |
| `Expires` / `Max-Age` | Persistent cookie; no expiry = session cookie |

`HttpOnly` + `Secure` + `SameSite=Strict` is the baseline for anything sensitive.

## CORS

Browsers block JavaScript from reading cross-origin responses unless the server explicitly allows it. This is **CORS** (Cross-Origin Resource Sharing).

Same origin = same scheme + host + port. `https://api.example.com` and `https://example.com` are different origins.

For **simple requests** (GET/POST with basic content types), the browser just adds an `Origin` header and checks the response:

```
Response: Access-Control-Allow-Origin: https://yourapp.com
```

For **non-simple requests** (DELETE, custom headers, `application/json` bodies), the browser sends a **preflight** OPTIONS request first:

```
OPTIONS /api/data HTTP/2
Origin: https://yourapp.com
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: Authorization
```

Server responds with what it allows:

```
Access-Control-Allow-Origin: https://yourapp.com
Access-Control-Allow-Methods: GET, POST, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
```

If the server doesn't respond with the right headers, the browser blocks the request — the network request still happens, the browser just won't give JavaScript the response.

`Access-Control-Allow-Credentials: true` allows cookies and auth headers on cross-origin requests. Can't be combined with `Access-Control-Allow-Origin: *`.

## Compression

Servers compress response bodies; clients say what they support in `Accept-Encoding`.

| Encoding | Notes |
| -------- | ----- |
| `gzip` | Widely supported, solid compression |
| `br` (Brotli) | Better compression than gzip, especially for text — use this when you can |
| `zstd` | Very fast, good compression — increasingly supported |
| `deflate` | Old, avoid |

Server adds `Content-Encoding: gzip` to indicate the body is compressed. Client decompresses transparently. Typical compression saves 60–80% on HTML/JSON/CSS.

## HTTP Versions

| Version | Transport | Key feature |
| ------- | --------- | ----------- |
| HTTP/1.0 | TCP | New connection per request |
| HTTP/1.1 | TCP | Persistent connections, pipelining (mostly unused), chunked transfer |
| HTTP/2 | TCP + TLS | Binary framing, multiplexing, header compression (HPACK), server push |
| HTTP/3 | QUIC (UDP) | Built-in encryption, eliminates TCP head-of-line blocking |

**HTTP/1.1** introduced `keep-alive` connections. Browsers work around its per-connection limitations by opening 6–8 parallel connections per origin.

**HTTP/2** multiplexes multiple requests over one connection — no need for multiple connections or domain sharding. Binary protocol, so no more text parsing. Header compression with HPACK cuts overhead significantly.

**HTTP/3** moves to QUIC, which runs over UDP. TLS 1.3 is baked in. Losing a packet in HTTP/2 stalls all streams on the TCP connection — HTTP/3 only stalls the one stream that lost the packet.

Check what version a site is running:

```bash
curl -I --http2 https://example.com
curl -I --http3 https://example.com
```
