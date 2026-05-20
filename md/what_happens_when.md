# What Happens When You Type google.com and Press Enter

A full request takes milliseconds. Here's everything happening under the hood.

## 1. Parsing the Input

The browser determines whether the input is a URL or a search query. If there's no scheme and no recognizable domain structure, the text is sent to the default search engine. `google.com` is a valid hostname, so the browser prepends `https://` and constructs `https://www.google.com/`.

If the hostname contains non-ASCII characters, the browser applies **Punycode encoding** to convert them to ASCII-compatible encoding. `münchen.de` becomes `xn--mnchen-3ya.de`.

## 2. HSTS Check

Before any network request, the browser checks its **HSTS (HTTP Strict Transport Security) preload list**. If `google.com` is on it, HTTPS is enforced immediately — no plain HTTP attempt, no redirect needed.

Websites can also set HSTS via response header without being on the preload list, but the first visit is then vulnerable to a downgrade attack.

## 3. DNS Resolution

The browser needs an IP address. It checks in order:

1. Browser DNS cache
2. OS DNS cache (`/etc/hosts` on Linux/macOS, hosts file on Windows)
3. Recursive resolver (your ISP or a public resolver like `8.8.8.8`)
4. Full recursive resolution: root → `.com` TLD → Google's authoritative nameserver

Google returns multiple A records (IPv4) and AAAA records (IPv6). The browser picks one — often racing IPv4 and IPv6 in parallel using **Happy Eyeballs** and connecting on whichever responds first.

## 4. ARP

Before the DNS query can even leave your machine, the network stack needs the MAC address of the next hop (your router). It checks the ARP cache first.

If there's no entry, it broadcasts an ARP request on the local network:

```
Who has 192.168.1.1? Tell 192.168.1.5
```

The router responds with its MAC address. That pairing is cached and the DNS query is sent. The same ARP process happens later when establishing the TCP connection to Google's IP, resolved to the router as the gateway.

## 5. TCP Connection

With an IP in hand, the browser opens a TCP connection to port 443.

Three-way handshake:
1. **SYN** — browser initiates
2. **SYN-ACK** — server acknowledges
3. **ACK** — browser confirms

This round trip adds latency. HTTP/2 and HTTP/3 reduce this over time through connection reuse.

## 6. Dropped Packets and Congestion Control

TCP doesn't assume the network is reliable. Before sending data, the browser starts with a small **congestion window** — a limit on how many unacknowledged bytes can be in flight.

- **Slow start** — window doubles for each acknowledged packet until a threshold is reached
- **Congestion avoidance** — after the threshold, window grows linearly
- **On packet loss** — window shrinks exponentially; sender backs off and retransmits

Modern Linux uses **CUBIC**; older systems use **New Reno**. If packets are dropped during the TLS handshake or early data transfer, this is why the page can stall briefly before loading.

## 7. TLS Handshake

HTTPS requires a TLS handshake over the TCP connection:

1. **ClientHello** — browser sends supported TLS versions, cipher suites, and a random value
2. **ServerHello** — server picks a cipher suite, sends its certificate and a random value
3. **Certificate verification** — browser validates the cert against trusted CAs, checks expiry, confirms the hostname matches
4. **Key exchange** — browser and server derive a shared session key (via ECDHE in modern TLS)
5. **Finished** — both sides confirm the handshake; encrypted communication begins

TLS 1.3 completes this in one round trip. TLS 1.2 takes two.

## 8. HTTP Request

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

If the browser has a cached copy and received an `ETag` previously, it sends an `If-None-Match` header. The server can then respond `304 Not Modified` with no body, and the browser serves the cached version.

## 9. Server-Side Processing

The request hits Google's infrastructure:

- **Anycast routing** already directed you to a nearby data center during DNS
- A **load balancer** distributes the request across backend servers
- **CDN edge nodes** may serve a cached response before the request reaches origin

At the origin, an HTTP daemon (nginx, Apache) receives the request and:

1. Parses the method, host, and path
2. Matches the request to a **virtual host** configuration
3. Checks IP, authentication, and access rules
4. Applies any **rewrite rules** (e.g., trailing slash normalization, URL routing)
5. Dispatches to the appropriate handler — static file, reverse proxy, or application runtime (PHP, Python, etc.)
6. Streams the response back

## 10. HTTP Response

The server responds:

```
HTTP/2 200 OK
Content-Type: text/html; charset=UTF-8
Content-Encoding: br
Strict-Transport-Security: max-age=31536000
...
```

The body is the HTML document, compressed with Brotli or gzip. The `Strict-Transport-Security` header tells the browser to remember HTTPS-only for the next year.

## 11. Browser Rendering

The browser receives the HTML in chunks (~8kB at a time) and starts parsing immediately without waiting for the full document.

### HTML Parsing

Builds the **DOM tree**. The HTML parser is fault-tolerant by spec — invalid markup is corrected, not rejected. Parsing is also reentrant: a `<script>` tag can modify the document mid-parse.

When parsing finishes, the document state moves to "interactive". Deferred scripts execute, then the `load` event fires.

### CSS Parsing

Each stylesheet is parsed into a **StyleSheet object** containing rules — each rule has a selector and a set of declarations. The browser builds the **CSSOM** (CSS Object Model) in parallel with the DOM.

### Render Tree

The DOM and CSSOM are combined into a **render tree** — only visible nodes are included (elements with `display: none` are excluded). Each node gets its computed style.

### Layout

The render tree is traversed to calculate exact positions and sizes:
- Width calculated bottom-up (child widths + margins/borders/padding)
- Width allocated top-down (parent distributes available space)
- Height calculated bottom-up (text wrapping + child heights)

Floated, absolutely positioned, and flexbox/grid elements are handled per W3C spec.

### Paint and Composite

Render objects issue drawing commands (fill, stroke, text). The page is split into **layers** — sections that can animate or scroll independently without re-rasterizing the whole page.

Layers are uploaded to the **GPU** as textures. The GPU handles the float-point calculations for compositing in parallel, which is why CSS transforms and opacity changes are cheap — they only trigger compositing, not layout or paint.

Final layer positions are computed and rendered via Direct3D or OpenGL. The GPU command buffer flushes asynchronously and the completed frame is sent to the window server.

## 12. Post-Rendering Execution

Rendering isn't the end. The browser continues executing JavaScript:

- **Timers** (`setTimeout`, `setInterval`, `requestAnimationFrame`) trigger additional code
- **User interactions** (scroll, click, hover) fire event handlers
- **Dynamic updates** — JS may fetch more data (XHR, fetch API), modify the DOM, and trigger new layout/paint cycles

For Google's homepage specifically, the search input gets focused, autocomplete listeners are attached, and a second round of requests may prefetch resources based on likely next actions.

## Full Timeline

| Step | What happens |
|------|-------------|
| 0ms | Enter pressed |
| ~1ms | URL parsed, HSTS checked |
| ~5ms | DNS resolved (cache hit) or ~50–100ms (full resolution) |
| ~6ms | ARP resolves gateway MAC |
| ~15ms | TCP connection established |
| ~25ms | TLS handshake complete (TLS 1.3) |
| ~30ms | HTTP GET sent |
| ~70ms | First byte received (TTFB) |
| ~100ms+ | Page renders, post-render JS executes |

Actual times vary by location, network, and server load.
