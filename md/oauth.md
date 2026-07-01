# OAuth & Auth Flows

OAuth2 is a framework for **authorization** — letting one service act on your behalf at another, without handing over your password. You've used it every time you clicked "Sign in with Google." What happens after that click is where security breaks.

## Key Concepts

| Term | What it means |
| ---- | ------------- |
| **Resource Owner** | The user. Owns the data. |
| **Client** | The app requesting access. |
| **Authorization Server** | Issues tokens. Google, GitHub, Auth0, etc. |
| **Resource Server** | The API that holds the data. Often the same server as the auth server. |
| **Scope** | What the client is asking permission for (`read:email`, `repo`, etc.) |
| **Access Token** | Short-lived credential the client uses to hit the API. |
| **Refresh Token** | Long-lived token used to get new access tokens without re-prompting the user. |

OAuth2 is about **authorization** (what you're allowed to do), not **authentication** (proving who you are). For authentication, you want OIDC on top of OAuth2.

## Grant Types

Different situations call for different flows. The right one depends on what kind of client you're building.

### Authorization Code (with PKCE)

The standard flow for web apps and mobile apps. You redirect the user to the auth server, they log in and consent, you get a code back, you exchange it for tokens.

**Without PKCE**, the code exchange is vulnerable if an attacker intercepts the redirect. **PKCE** (Proof Key for Code Exchange) fixes this.

Flow:

1. Client generates a random `code_verifier`, hashes it to get `code_challenge`
2. Redirect user to the auth server:
   ```
   https://auth.example.com/authorize
     ?response_type=code
     &client_id=abc123
     &redirect_uri=https://yourapp.com/callback
     &scope=openid email
     &state=randomvalue
     &code_challenge=BASE64URL(SHA256(code_verifier))
     &code_challenge_method=S256
   ```
3. User logs in and approves
4. Auth server redirects to `redirect_uri?code=AUTH_CODE&state=randomvalue`
5. Client verifies `state` matches what it sent (CSRF protection)
6. Client POSTs to the token endpoint:
   ```
   POST /token
   grant_type=authorization_code
   &code=AUTH_CODE
   &redirect_uri=https://yourapp.com/callback
   &client_id=abc123
   &code_verifier=ORIGINAL_VERIFIER
   ```
7. Auth server verifies the code_verifier hashes to the stored code_challenge
8. Returns access token + refresh token + (if OIDC) ID token

Use this for: any app where a user is present.

### Client Credentials

No user involved. The client authenticates as itself — useful for machine-to-machine communication.

```
POST /token
grant_type=client_credentials
&client_id=abc123
&client_secret=secret
&scope=read:data
```

Returns an access token. No refresh token (just request a new one when it expires).

Use this for: backend services, cron jobs, APIs talking to other APIs.

### Device Code

For devices without a browser — smart TVs, CLIs, IoT devices. The device gets a code and tells the user to go approve it on another device.

1. Device POSTs to `/device/code`, gets back a `device_code`, `user_code`, and `verification_uri`
2. Device shows: "Go to example.com/activate and enter: ABCD-1234"
3. Device polls `/token` every few seconds with `grant_type=urn:ietf:params:oauth:grant-type:device_code`
4. Once user approves, polling returns tokens

Use this for: CLIs (`gh auth login`), TV apps, anything without a browser.

### Implicit (deprecated)

Returned tokens directly in the redirect URL fragment. Convenient but insecure — tokens end up in browser history and server logs. Don't use it. Use Authorization Code + PKCE instead.

## Tokens

### Access Tokens

Short-lived (minutes to hours). Passed as a Bearer token in the Authorization header:

```
Authorization: Bearer eyJhbGci...
```

The resource server validates the token on every request — either by checking a local signature (if it's a JWT) or calling the auth server's introspection endpoint.

### Refresh Tokens

Long-lived (days to months). Stored server-side or in secure storage. Used only to get new access tokens:

```
POST /token
grant_type=refresh_token
&refresh_token=REFRESH_TOKEN
&client_id=abc123
```

Rotate refresh tokens on each use — each new token invalidates the previous one.

### JWTs

Most access tokens are JWTs (JSON Web Tokens). Three base64url-encoded parts, separated by dots:

```
HEADER.PAYLOAD.SIGNATURE
```

**Header** — algorithm and token type:
```json
{ "alg": "RS256", "typ": "JWT" }
```

**Payload** — claims (data):
```json
{
  "sub": "user123",
  "iss": "https://auth.example.com",
  "aud": "your-api",
  "exp": 1720000000,
  "iat": 1719996400,
  "scope": "read:email"
}
```

**Signature** — HMAC or RSA/ECDSA signature over the header + payload. The resource server verifies this without calling the auth server.

| Claim | Meaning |
| ----- | ------- |
| `sub` | Subject — who the token is about |
| `iss` | Issuer — who issued it |
| `aud` | Audience — who it's intended for |
| `exp` | Expiration timestamp |
| `iat` | Issued-at timestamp |
| `jti` | Unique token ID (useful for revocation) |

JWTs are **not encrypted by default** — anyone can base64-decode the payload. Don't put secrets in them. Use JWE if you need encryption.

## OpenID Connect (OIDC)

OAuth2 handles authorization but says nothing about who the user is. **OIDC** is a thin layer on top that adds authentication.

It introduces the **ID token** — a JWT containing claims about the user (name, email, picture, etc.). It also adds a standard `/userinfo` endpoint you can hit with an access token.

If you're doing "Sign in with X" — you're using OIDC. The key scopes to request: `openid`, `profile`, `email`.

## Token Storage

Where you store tokens matters a lot.

| Storage | XSS risk | CSRF risk | Notes |
| ------- | -------- | --------- | ----- |
| `localStorage` | High | Low | Accessible from JS — any XSS attack can steal tokens |
| `sessionStorage` | High | Low | Same as localStorage, cleared on tab close |
| Memory (JS variable) | Low | Low | Gone on refresh; best for access tokens in SPAs |
| HttpOnly cookie | None | Medium | JS can't read it; use `SameSite=Strict` or CSRF tokens to mitigate CSRF |

For SPAs: keep access tokens in memory, use a backend-for-frontend (BFF) pattern with HttpOnly cookies for refresh tokens. For mobile: use the OS secure credential store (Keychain on iOS, Keystore on Android).

## Security

Use PKCE for every Authorization Code flow, even for confidential clients. Validate `state` on the callback — that's your CSRF protection. When accepting JWTs, check `aud` (a token issued for another API shouldn't work on yours) and always check `exp`. Keep access tokens short-lived — minutes, not hours. Lock `redirect_uri` to exact matches, no wildcards. And HTTPS everywhere: a token sent in plaintext is a token anyone on the path can read.
