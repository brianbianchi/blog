# Broken Authentication

Authentication is the process of proving you are who you say you are. When it breaks, the consequences are direct: someone else can prove they're you. Broken authentication covers a wide range of failures, from weak passwords and predictable session tokens to flawed reset flows and missing multi-factor authentication. Understanding it means looking at the whole lifecycle of an authenticated session, not just the login form.

## Session Tokens: The Core Concept

When you log in to a web application, the server needs a way to recognize you on subsequent requests. HTTP is stateless; it has no memory. The solution is a session token: a credential the server issues after authentication that the client sends with every request.

A session token is only as good as its unpredictability. If an attacker can guess or forge a valid token, they bypass authentication entirely without ever needing the underlying password.

**What makes a good token:**
- Generated from a cryptographically secure random number generator (not `Math.random()`, not timestamps, not sequential IDs)
- Long enough to make brute force infeasible: 128 bits of entropy is a common recommendation
- Invalidated server-side on logout
- Rotated on privilege changes (especially on login)

**Where tokens live:**
- `Cookie` header: the traditional approach, with security flags available (`HttpOnly`, `Secure`, `SameSite`)
- `Authorization` header with a Bearer token: common in APIs and SPAs, stored in memory or localStorage
- Hidden form fields: rarely a good idea for sessions

localStorage is convenient but exposes tokens to JavaScript, meaning any XSS vulnerability can steal them. Cookies with `HttpOnly` block JavaScript access at least, which is one point in their favor.

## Session Fixation

Session fixation is a subtler attack than hijacking. The attacker doesn't steal a session; they set one.

Here's how it works: some applications assign a session ID before authentication and keep it after login. An attacker visits the login page, notes the pre-authentication session ID, then tricks the victim into logging in using that same ID (by sending them a crafted URL with the session ID embedded, for example). After the victim authenticates, their session is now the one the attacker already knows.

The fix is simple: regenerate the session ID immediately upon successful login. The pre-auth session ID should be thrown away and replaced with a fresh one. Most frameworks handle this automatically if you use their session management properly, but custom implementations often get this wrong.

## Session Hijacking

Once an attacker has a valid session token, they're authenticated. The question is how they get it.

**XSS**: If the session cookie doesn't have the `HttpOnly` flag, `document.cookie` reveals it. Even with `HttpOnly`, XSS can still make authenticated requests on the user's behalf.

**Network sniffing**: If the application runs over plain HTTP, anyone on the same network (especially relevant on public Wi-Fi) can read cookie values from unencrypted traffic. This is why the `Secure` cookie flag matters: it ensures the cookie is only sent over HTTPS.

**Predictable tokens**: If someone rolled their own session ID generator using a timestamp or sequential counter, an attacker can simply enumerate tokens. This was embarrassingly common in older PHP applications.

**Stolen via logs or referrer**: If a session token ends up in a URL parameter instead of a cookie, it may appear in access logs, browser history, or `Referer` headers sent to third-party resources.

## Credential Stuffing

Every major breach produces a list of username/password pairs. Those lists are available to anyone who wants them. Credential stuffing is the practice of automating login attempts using those lists against other sites, betting that users reused their passwords.

It's highly effective because password reuse is endemic. A breach at a gaming forum might yield valid credentials for someone's banking account. The attacker doesn't need to exploit any vulnerability in the target application; they just need working credentials.

Defenses: rate limiting login attempts, CAPTCHA on repeated failures, MFA (a reused password is useless if MFA is required), and monitoring for distributed low-rate login attempts that slip under per-IP thresholds.

## Brute Force Attacks

Brute force is the blunt version of the credential attack: try every combination, or try a dictionary of common passwords, against a specific account.

Defenses, roughly in order of effectiveness:

| Defense | Notes |
|---|---|
| Account lockout | Locks out after N failures. Watch out for account enumeration if the error message distinguishes locked from invalid. Also enables denial-of-service against legitimate users if not designed carefully. |
| Rate limiting | Slower than lockout to stop, but avoids the DoS issue. Combine with exponential backoff. |
| CAPTCHA | Stops automated attacks. Annoying for real users. Best as a secondary trigger after failed attempts. |
| MFA | Even a correct password is insufficient without the second factor. The most robust option. |

Progressive delays are worth considering: don't lock the account after 10 attempts, just make each subsequent attempt wait a bit longer. It stops automation without permanently locking out users.

## Default Credentials

Network devices, applications, and management consoles often ship with default credentials (`admin`/`admin`, `admin`/`password`, etc.). A surprising number of them end up internet-exposed with those credentials unchanged. Shodan makes it trivial to find them.

This isn't just a home router problem. Default credentials in enterprise VPN appliances, industrial control systems, and cloud management interfaces have all led to significant breaches. Forcing credential change on first use is table stakes; it's remarkable how many products still don't.

## Insecure "Remember Me" Implementations

"Remember me" functionality extends a session beyond the browser session. Done well, it issues a long-lived, cryptographically random token stored in a persistent cookie, tied to the user server-side and invalidated on logout or password change.

Done poorly, it might store the username and password in a cookie (sometimes base64-encoded, which is not encryption), use a predictable "remember me" token, or fail to invalidate the token when the user changes their password.

A common mistake is a persistent token that never expires and can't be revoked individually (e.g., "forget all remembered devices"). If that token is stolen, there's no way to invalidate it without changing the password.

## Password Reset Flaws

Reset flows are frequently weak and frequently targeted.

**Predictable reset tokens**: A token based on the timestamp, a hash of the email address, or sequential numbers can be guessed. Reset tokens must be cryptographically random.

**No expiry**: A reset link that works a week later is a problem. Short expiry windows (15-60 minutes) limit the window for exploitation.

**User enumeration**: "We've sent a reset email if that address exists" is the correct message. "That email isn't registered" tells an attacker who has an account. The response time should also be the same regardless of whether the address exists (beware of timing attacks).

**Token in URL only**: If the reset token is in the URL and the page loads third-party resources, the token may leak in `Referer` headers. Consider POST-based reset confirmation flows.

**Security questions**: These are not a real second factor. Mother's maiden name, high school mascot, and first pet are all findable. Security questions should not be the sole mechanism for account recovery.

## Multi-Factor Authentication

MFA requires something you know (password) plus something you have or are. The second factor makes credential-only attacks largely useless.

**TOTP (Time-based One-Time Password)**: An authenticator app (Google Authenticator, Authy, etc.) generates a six-digit code by computing HMAC-SHA1 of a shared secret combined with the current Unix timestamp divided into 30-second windows. The server knows the same secret and generates the same code. The code is only valid for that 30-second window (with a bit of tolerance for clock skew).

This is the RFC 6238 standard. It doesn't require a network connection to generate codes, which is a usability win. The security depends on keeping the shared secret safe: if it's leaked, an attacker can generate valid codes indefinitely.

**SMS-based OTP**: A code is texted to your phone number. The significant weakness here is SIM swapping: an attacker convinces a mobile carrier to transfer your phone number to their SIM card. This is social engineering against carrier support staff, and it has been used in high-profile attacks. SMS OTP is substantially better than no MFA, but it's the weakest MFA option.

**Authenticator apps over SMS is a meaningful upgrade**, not just a marginal one. Organizations dealing with sensitive data or high-value accounts should push users toward app-based TOTP or hardware keys.

**Hardware keys (FIDO2/WebAuthn)**: The strongest option. Phishing-resistant by design because the key's response is bound to the specific origin. Not yet ubiquitous, but worth supporting.

## Prevention Checklist

- Generate session IDs using a CSPRNG with at least 128 bits of entropy
- Regenerate the session ID immediately after successful login
- Set `HttpOnly`, `Secure`, and `SameSite=Strict` (or `Lax` where Strict is too restrictive) on session cookies
- Invalidate sessions server-side on logout; don't just delete the client-side cookie
- Enforce rate limiting and/or account lockout on authentication endpoints
- Use consistent error messages that don't reveal whether an account exists
- Set short expiry on password reset tokens and invalidate them after use
- Require MFA for sensitive accounts, and prefer TOTP or hardware keys over SMS
- Never store passwords in plaintext; use bcrypt, scrypt, or Argon2 with appropriate cost factors
- Monitor for credential stuffing: watch for distributed login attempts from many IPs with valid-looking credentials
