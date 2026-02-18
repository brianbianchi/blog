# Common OWASP risks

The OWASP Top 10 is a community–driven list of the most critical web application security risks, updated to reflect how real‑world apps are actually being attacked and misconfigured today. Each item below summarizes the risk and gives practical protection steps developers can apply in everyday work.

***

## A01: Broken access control

*Broken access control* occurs when users can act outside of what their role or identity should allow—seeing other users’ data, performing admin actions, or calling APIs they should not. This often comes from missing authorization checks, insecure object references (like `/api/user/123` exposing someone else’s account), or relying only on client‑side controls.

Attackers abuse broken access control to:

- View or edit other users’ profiles, orders, or documents.
- Escalate to admin or support roles by guessing or modifying IDs.
- Access internal APIs that were never meant for the public internet.

### Protection

- Enforce authorization on every request on the server side, not just in the UI.
- Prefer a **centralized** authorization component or middleware over hand‑rolled checks.
- Use “deny by default”: endpoints should be inaccessible unless explicitly allowed.
- Avoid exposing direct object IDs; use indirect references and verify ownership for each object.

***

## A02: Security misconfiguration

*Security misconfiguration* is when an application or infrastructure is deployed with insecure defaults, unnecessary features, or missing hardening steps. Examples include verbose error messages, directory listings, default passwords, and wide‑open CORS policies.

Misconfiguration lets attackers:

- Discover internal details and stack traces from error pages.
- Abuse admin panels protected only by default credentials.
- Exploit weak TLS/cipher settings or wide network exposure.

### Protection

- Use hardened, version‑controlled baseline configs for servers, containers, and frameworks.
- Disable features you don’t use (debug modes, test endpoints, verbose logging in production).
- Rotate and remove default credentials; integrate secrets management.
- Automate configuration checks in CI/CD (linting, policy‑as‑code, security scanners).

***

## A03: Software supply chain failures

*Software supply chain failures* cover risks introduced via dependencies, build pipelines, package registries, and distribution channels, not just a single outdated library. Compromised packages, tampered artifacts, or malicious updates can silently infect many applications at once.

These failures can lead to:

- Malicious code executing inside your app or CI system.
- Credential theft from build servers or deployment environments.
- Backdoored releases shipped to all customers.

### Protection

- Maintain a **software bill of materials (SBOM)** listing all dependencies and versions.
- Pin dependency versions and use trusted registries and mirrors.
- Sign and verify build artifacts; use reproducible builds where feasible.
- Isolate build infrastructure, restrict who and what can change pipelines, and enable code review for pipeline definitions.

***

## A04: Cryptographic failures

*Cryptographic failures* occur when apps store or transmit sensitive data without proper encryption or use broken/weak algorithms, keys, or protocols. Common issues include unencrypted HTTP, home‑grown crypto, weak key management, or storing passwords in plain text.

Attackers can then:

- Intercept and read traffic (e.g., over open Wi‑Fi).
- Decrypt stored data after a breach, including credentials and personal data.
- Forge tokens or session cookies if keys are exposed.

### Protection

- Use HTTPS everywhere; enforce HSTS and secure cookies.
- Rely on modern, vetted algorithms and libraries—never invent your own crypto.
- Hash passwords with strong algorithms (like bcrypt, scrypt, or Argon2) and per‑user salts.
- Store keys and secrets in dedicated secret‑management services, with rotation and access control.

***

## A05: Injection

*Injection* vulnerabilities appear when untrusted data is sent to an interpreter (SQL, NoSQL, OS shell, LDAP, template engines, etc.) as part of a command or query. If input is concatenated directly into commands, attackers can change the query’s meaning. [owasp](https://owasp.org/www-project-top-ten/)

Attackers use injection to:

- Access or modify database records (SQL/NoSQL injection).
- Execute OS commands and gain remote code execution.
- Alter template rendering to leak secrets or run arbitrary code.

### Protection

- Use parameterized queries and prepared statements for all database access.
- Avoid building shell commands with string concatenation; prefer safe APIs.
- Apply server‑side input validation and strict allowlists for expected formats.
- Run interpreters and database processes with least privilege and strong isolation.

***

## A06: Insecure design

*Insecure design* is about flaws in the system’s **architecture**, not just bugs in code. Even perfectly implemented code is vulnerable if the underlying design ignores threat models, abuse cases, or defense‑in‑depth.

This often shows up as:

- Critical operations without multi‑factor verification or workflow approvals.
- Single points of failure where one compromise leads to full account takeover.
- Business logic paths that can be replayed, bypassed, or automated at scale.

### Protection

- Perform threat modeling early in projects and at major design changes.
- Design security controls (rate limits, workflow checks, approvals) as first‑class requirements.
- Use defense‑in‑depth: layers of checks, monitoring, and segregation of duties.
- Revisit designs after incidents and pen tests to close systemic gaps.

***

## A07: Authentication failures

*Authentication failures* (previously “broken authentication”) occur when identity verification is weak, incorrectly implemented, or easy to bypass. Examples include weak password policies, missing MFA, insecure session handling, and predictable password reset flows.

Resulting attacks include:

- Credential stuffing and brute‑force logins with leaked password lists.
- Session hijacking via stolen or predictable session tokens.
- Account takeover through insecure “forgot password” flows.

### Protection

- Enforce MFA for high‑value accounts and admin access.
- Use resilient password storage and rate limiting on login and reset attempts.
- Implement secure session management: random IDs, secure and HttpOnly cookies, proper session invalidation on logout and privilege changes.
- Use well‑tested authentication frameworks and identity providers instead of custom schemes.

***

## A08: Software or data integrity failures

These failures happen when code, updates, configuration, or critical data can be altered without detection or proper integrity checks. Typical issues include unsigned updates, unverified plugins, or dynamic loading of code from untrusted sources.

Attackers can:

- Inject malicious modules or scripts into update channels.
- Modify configuration or rules (e.g., access lists, pricing rules) to gain advantage.
- Tamper with logs or audit trails to hide their activity.

### Protection

- Sign and verify code, containers, and configuration artifacts.
- Restrict who can change production configuration; enforce approvals and change history.
- Avoid loading code from remote domains at runtime unless strictly validated.
- Use write‑once or append‑only logging for critical systems and security events.

***

## A09: Logging and alerting failures

When *logging and alerting* are missing or incomplete, attacks go unnoticed, and incident response is slow or impossible. This isn’t just about collecting logs; it’s about capturing the *right* events and acting on them.

Consequences include:

- Breaches detected months later, if at all.
- Inability to reconstruct what happened during an incident.
- Missed opportunities to block ongoing attacks or compromised accounts.

### Protection

- Log security‑relevant events: logins, failures, permission changes, key API actions.
- Centralize logs and protect them from tampering; use correlation and retention policies.
- Configure alerts for suspicious behavior (e.g., login anomalies, repeated failures, mass downloads).
- Regularly rehearse incident response so teams know how to react when alerts fire.

***

## A10: Mishandling of exceptional conditions

*Mishandling of exceptional conditions* covers failures to deal safely with errors, timeouts, resource exhaustion, race conditions, and other abnormal states. Poor error handling often leaks implementation details, leaves partial operations in inconsistent states, or causes security checks to “fail open.”

Attackers exploit this by:

- Triggering edge cases that bypass validation or authorization.
- Causing denial of service through resource exhaustion or unbounded retries.
- Using detailed error messages to map the architecture and find new weaknesses.

### Protection

- Treat error handling and timeouts as part of security design, not an afterthought.
- Avoid exposing stack traces or internal details to end users; return generic messages instead.
- Ensure operations are atomic or compensating (either fully applied or fully rolled back).
- Use safe defaults on failure: if in doubt, deny access and log the condition.

***