# How Public Key Infrastructure Works

Asymmetric cryptography gives you a way to encrypt data for someone using their public key, with only their private key able to decrypt it. That's powerful. But it rests on a question that's easy to overlook: how do you know the public key you have actually belongs to who you think it does?

If you want to send an encrypted message to your bank, and an attacker can intercept your connection and substitute their own public key, you've just encrypted your data for the attacker. The cryptography works perfectly; the problem is that you trusted the wrong key. This is a man-in-the-middle attack at the identity layer.

Public Key Infrastructure (PKI) is the system built to solve that problem. It ties public keys to verified identities through a chain of trust.

## Certificates

The core unit of PKI is the **X.509 certificate**. A certificate is a document that says: "This public key belongs to this entity." It contains:

- **Subject:** Who the certificate was issued to (e.g., `CN=example.com`)
- **Issuer:** Who issued and signed the certificate
- **Public key:** The subject's public key
- **Validity period:** Not-before and not-after dates
- **Serial number:** Unique identifier for the certificate
- **Subject Alternative Names (SANs):** Additional domains or IP addresses the certificate is valid for
- **Signature:** The issuer's digital signature over the rest of the certificate

The signature is what matters. When a trusted authority signs a certificate, they're vouching that they verified the subject's identity. Anyone who trusts that authority can verify the signature and, by extension, trust the certificate.

## Certificate Authorities

A **Certificate Authority (CA)** is an organization trusted to issue certificates after verifying identities. When a CA signs a certificate, they're asserting: "We checked, and this public key really does belong to this entity."

CAs are arranged in a hierarchy:

**Root CAs** are the anchors of trust. Their certificates are self-signed (they vouch for themselves) and are embedded directly in operating systems and browsers. There are relatively few of them, and they're operated with extreme care. The private key of a root CA is kept offline and used only to sign intermediate CA certificates.

**Intermediate CAs** sit between the root and the end-entity certificates. If an intermediate CA's private key is compromised, the root CA can revoke just that intermediate's certificate rather than having to replace every certificate in its entire tree. This limits blast radius. In practice, almost all certificates you encounter on websites are issued by intermediates.

When you connect to a website, the server presents its certificate along with the intermediate CA's certificate. Your browser builds the **chain of trust** from the server certificate up through the intermediate to a root CA it recognizes.

## How a Browser Validates a Certificate

Certificate validation is a multi-step process, and browsers do it automatically. Understanding what they're checking is useful.

1. **Chain building:** The browser traces the certificate chain from the server certificate up through the issuing CA to a root CA. Each certificate in the chain must be properly signed by the next one up.

2. **Root trust:** The root CA at the top of the chain must be in the browser's (or OS's) trust store. Windows ships with a set of trusted roots; so does macOS, Firefox, and most mobile operating systems. If the root isn't in the trust store, the chain can't be validated.

3. **Validity period:** Each certificate in the chain must have a not-before date in the past and a not-after date in the future.

4. **Name matching:** The hostname you're connecting to must match either the Common Name or one of the SANs in the certificate.

5. **Revocation checking:** The browser checks whether any certificate in the chain has been revoked before its expiry.

If any of these checks fail, the browser shows an error. The specific error matters: an expired certificate is different from an untrusted issuer.

## Revocation: CRL and OCSP

Certificates have expiration dates, but sometimes a certificate needs to be invalidated before it expires. Maybe the private key was compromised, or the business closed, or the certificate was issued incorrectly. Two mechanisms handle this:

**CRL (Certificate Revocation List):** A signed list published by the CA of all the serial numbers it has revoked. Clients can download the CRL and check against it. The problem with CRLs is that they can get large, they're periodically updated (so there's a window where a revoked cert still looks valid), and downloading them adds latency.

**OCSP (Online Certificate Status Protocol):** A client queries the CA's OCSP responder with a specific certificate's serial number and gets back a signed response: good, revoked, or unknown. This is faster than downloading a full CRL, but it introduces a privacy issue (the CA sees which sites you're visiting) and a reliability dependency (the OCSP responder has to be reachable).

**OCSP stapling** addresses both problems. The server periodically fetches a fresh OCSP response for its own certificate and includes (staples) it in the TLS handshake. The client gets revocation status without making a separate network call or revealing anything to the CA.

In practice, revocation checking has historically been unreliable enough that most browsers use a "soft fail" model: if the revocation check fails, they proceed anyway. This is a known problem in the ecosystem.

## Certificate Pinning

Normally, any trusted CA can issue a certificate for any domain. That's a broad trust surface. **Certificate pinning** lets an application restrict which certificates or public keys it will accept for a specific domain.

A mobile app might be hardcoded to only accept connections where the server certificate was issued by a specific intermediate CA, or where the server's public key matches a specific value. Even if an attacker somehow got a certificate for that domain from a different trusted CA, the pin would reject it.

The downside is operational: if you pin to a specific certificate and that certificate rotates, your app breaks until it's updated. Pinning to a public key (rather than a full certificate) and maintaining a backup pin mitigates this, but it still requires care. Browsers themselves moved away from broad certificate pinning for external sites (HTTP Public Key Pinning, or HPKP, was deprecated in 2018) partly because misconfiguration was bricking sites.

## Self-Signed Certificates

A self-signed certificate is one where the issuer and subject are the same entity. There's no third party vouching for the identity. The certificate is mathematically valid, but it has no chain to a trusted root.

Browsers warn on self-signed certificates because they can't verify who created them. An attacker performing a man-in-the-middle attack could present a self-signed certificate, and without the warning, a user might not notice. The warning is the browser saying: "I can verify the encryption is happening, but I can't tell you who you're talking to."

Self-signed certificates are fine for internal services where you control both the client and server configuration and can distribute the certificate out-of-band, or for development environments. They're not appropriate for anything public-facing.

## Let's Encrypt and HTTPS Everywhere

Before Let's Encrypt launched in 2016, getting a certificate meant paying a CA, going through a validation process, and manually installing and renewing a file. Certificates cost money and renewal was manual, so plenty of sites ran on HTTP or used expired certificates.

Let's Encrypt is a free, automated, and open CA run by the nonprofit ISRG. It issues Domain Validated (DV) certificates, which verify that you control the domain, but don't verify your organization's identity. For most websites, that's sufficient. The ACME protocol allows automated issuance and renewal; tools like Certbot handle the whole process with a single command. Certificates are valid for 90 days and renewal is automatic.

The result is that running HTTPS has essentially zero marginal cost. The share of web traffic encrypted with TLS has gone from around 50% in 2016 to over 95% now. That's a meaningful shift.

## Common Attacks and Failures

**Expired certificates:** Simple to fix, surprisingly common. An expired certificate doesn't just cause a browser warning; it means your certificate was issued before the validation was current, and the CA is no longer vouching for it. Monitor expiration dates and automate renewal.

**Misconfigured SANs:** If a certificate for `www.example.com` doesn't include `example.com` in the SANs, visiting the bare domain will throw a name mismatch error. Also, wildcard certificates (`*.example.com`) cover one level of subdomain but not the apex domain and not sub-subdomains. These details cause real outages.

**Rogue CAs:** Since any trusted CA can issue a certificate for any domain, a compromised or malicious CA is a serious threat. The DigiNotar breach in 2011 is the textbook case. DigiNotar, a Dutch CA, was compromised and the attacker issued fraudulent certificates for Google, Mozilla, and others. Those certificates were used to intercept the communications of hundreds of thousands of Iranians. DigiNotar was removed from all trust stores within days and went bankrupt shortly after. The incident accelerated work on **Certificate Transparency (CT)**, a system where all publicly-trusted CAs are required to log every certificate they issue to publicly-auditable logs. CT doesn't prevent misissuance, but it makes it detectable.

**Short-lived certificate exposure:** Even a legitimately-issued certificate can be dangerous if the private key is stolen. An attacker with the private key can impersonate the server until the certificate expires or is revoked. This is why protecting the private key and keeping it off disk where possible (hardware security modules are the right answer for high-value keys) matters.

PKI is a system built on trust. Understanding where that trust comes from, and where it can break down, is what lets you use it well.
