# MITRE ATT&CK Explained

Before ATT&CK, there was no shared vocabulary for describing attacker behavior. Security teams, vendors, and researchers all described the same techniques in different terms. You couldn't easily compare what one red team found to what another red team found, or map a detection rule to a specific attacker behavior in a meaningful way. ATT&CK fixed that.

## What It Is

MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge) is a knowledge base of adversary tactics, techniques, and procedures (TTPs) based on real-world observations of actual attacks. MITRE built it by analyzing threat intelligence reports, malware analyses, red team engagements, and incident reports, then categorizing and documenting what attackers actually do.

It's a living document. New techniques are added as new attack behaviors are observed and reported. The current Enterprise matrix has over 200 techniques and nearly 450 sub-techniques.

The framework is freely available at attack.mitre.org. There are matrices for Enterprise (Windows, macOS, Linux, cloud, containers, network), Mobile (iOS, Android), and ICS (industrial control systems).

## Tactics, Techniques, and Sub-Techniques

Understanding the three-level hierarchy is the key to using ATT&CK effectively.

**Tactics** are the adversary's goals at each stage of an intrusion. They answer "why." Getting initial access is a tactic. Maintaining persistence is a tactic. Exfiltrating data is a tactic. There are 14 enterprise tactics, and they roughly map to a progression through an attack, though attackers don't always follow them linearly.

**Techniques** are the "how." A technique is a specific method used to accomplish a tactical goal. Phishing is a technique for achieving Initial Access. Credential dumping is a technique for Credential Access. Each technique has a T-number identifier.

**Sub-techniques** are more specific implementations of a technique. T1059 (Command and Scripting Interpreter) has sub-techniques for PowerShell (T1059.001), Windows Command Shell (T1059.003), Python (T1059.006), and several others. Sub-techniques let you be precise without fragmenting the taxonomy into thousands of top-level entries.

## The 14 Enterprise Tactics

| # | Tactic | What the Attacker Is Doing |
|---|--------|---------------------------|
| 1 | Reconnaissance | Gathering information before attacking: researching the target, finding email addresses, mapping infrastructure |
| 2 | Resource Development | Building attack infrastructure: registering domains, setting up C2 servers, acquiring tools, compromising third-party accounts |
| 3 | Initial Access | Getting a foothold: phishing, exploiting a public-facing application, supply chain compromise, valid accounts |
| 4 | Execution | Running malicious code: PowerShell, cmd.exe, scheduled tasks, WMI, user execution (tricking someone into running something) |
| 5 | Persistence | Surviving restarts and credential changes: registry run keys, services, scheduled tasks, new accounts, web shells |
| 6 | Privilege Escalation | Getting higher privileges: exploiting misconfigurations, token impersonation, Kerberos abuse, DLL hijacking |
| 7 | Defense Evasion | Avoiding detection: disabling security tools, clearing logs, obfuscating commands, living off the land |
| 8 | Credential Access | Stealing credentials: LSASS dumping, Kerberoasting, keylogging, credential files, NTLM relay |
| 9 | Discovery | Learning the environment: enumerating users, groups, processes, network shares, trust relationships |
| 10 | Lateral Movement | Moving to other systems: pass-the-hash, RDP, PsExec, WMI, SMB |
| 11 | Collection | Gathering data to steal: keylogging, screen capture, accessing email, staging files |
| 12 | Command and Control | Maintaining communication with compromised systems: beaconing over HTTPS, DNS tunneling, using legitimate cloud services for C2 |
| 13 | Exfiltration | Getting data out: over C2 channels, to cloud storage, via email, with compression and encryption |
| 14 | Impact | Achieving the end goal: ransomware, data destruction, defacement, service disruption |

Reconnaissance and Resource Development are the pre-attack phases. Many defenders focus primarily on techniques from Initial Access onward, which is reasonable given that pre-attack activity often happens outside the defender's visibility. But threat intelligence teams track Reconnaissance activity and can sometimes identify when an organization is being targeted before the attack begins.

## Well-Known Techniques

A few techniques worth knowing by ID because they come up constantly:

**T1566 (Phishing)**: The most common initial access vector. Sub-techniques cover spearphishing attachments, links, and service-based phishing. Nearly every major breach involves phishing somewhere in the chain.

**T1078 (Valid Accounts)**: Using legitimate credentials to access systems. This is why credential theft and initial access are so closely linked. An attacker with valid credentials is often indistinguishable from a legitimate user.

**T1059 (Command and Scripting Interpreter)**: Running malicious commands via scripting engines. PowerShell (T1059.001) is particularly popular because it's powerful, built into Windows, and can download and execute code directly from memory.

**T1053 (Scheduled Task/Job)**: Creating scheduled tasks or cron jobs for execution or persistence. Very common because it's a legitimate OS feature and the artifacts can be subtle.

**T1003 (OS Credential Dumping)**: Extracting credentials from memory or storage. Sub-techniques cover LSASS memory (Mimikatz), SAM database, NTDS.dit (domain controller credential store), and others.

**T1021 (Remote Services)**: Lateral movement via remote access protocols. Sub-techniques cover RDP (T1021.001), SMB/Windows Admin Shares (T1021.002), SSH (T1021.004), and WinRM (T1021.006).

## ATT&CK Navigator

The Navigator is a web-based tool (available at mitre-attack.github.io/attack-navigator) that lets you work with the ATT&CK matrix visually. You can:

- Color-code techniques to show which ones you have detections for (coverage mapping)
- Layer multiple matrices to compare attacker groups or campaigns
- Export and share annotated matrices
- Import threat intelligence to see which techniques a specific threat actor uses

Defenders use Navigator to visualize detection coverage gaps. You can map your SIEM rules, EDR capabilities, and other controls to specific techniques, then see which parts of the matrix have no coverage. That's where the next detection engineering effort should focus.

Red teams use it to plan engagements. Rather than ad-hoc testing, a well-structured red team engagement maps each action to an ATT&CK technique, which produces a report that's directly comparable to detection coverage and communicates findings in terms defenders can act on.

## How Red Teams Use ATT&CK

ATT&CK gives red teams a structured vocabulary for planning and reporting. Before an engagement, the team can decide which technique categories to exercise based on what the client's threat model looks like. An organization facing financially motivated ransomware groups warrants different technique coverage than one concerned about nation-state espionage.

During the engagement, documenting each action by technique ID makes the final report immediately useful. A finding that says "we were able to dump credentials using T1003.001 (LSASS Memory) and move laterally via T1021.002 (SMB/Windows Admin Shares) without triggering an alert" tells the blue team exactly where the detection gap is.

## How Blue Teams Use ATT&CK

For defenders, ATT&CK is primarily a tool for structured gap analysis. The process looks like this:

1. Enumerate your existing detection capabilities (SIEM rules, EDR behavioral detections, etc.)
2. Map each capability to the ATT&CK technique it covers
3. Look at the matrix and identify which techniques have no coverage
4. Prioritize based on what threat actors targeting your industry actually use (ATT&CK groups and campaigns data helps here)
5. Build detections for the highest-priority gaps

ATT&CK also provides detection notes for each technique, including relevant data sources and suggested queries. These aren't copy-paste detections, but they're a useful starting point.

## ATT&CK vs Cyber Kill Chain

The Lockheed Martin Cyber Kill Chain is a seven-phase linear model: Reconnaissance, Weaponization, Delivery, Exploitation, Installation, Command and Control, Actions on Objectives. It came first and was widely adopted.

ATT&CK is a matrix, not a chain. Real attacks aren't linear; attackers loop back, skip phases, and pursue multiple objectives simultaneously. The Kill Chain's linearity is both a strength (easy to explain) and a weakness (doesn't reflect reality well).

They're complementary. The Kill Chain is useful for explaining the general shape of an intrusion to executives and non-technical stakeholders. ATT&CK is more useful for the specific, detailed work of detection engineering and red team planning. Many organizations use both.

## Limitations

ATT&CK reflects documented, public knowledge. Techniques used in attacks that haven't been publicly reported aren't in the database yet. Novel attack methods, classified government operations, and techniques used by actors who haven't been written about publicly are all absent.

Don't treat complete ATT&CK coverage as "done." Covering every documented technique is an ambitious goal, and pursuing it could lead to building detections for techniques that are obscure and rarely used while gaps remain for common, high-impact ones. Prioritization based on real threat intelligence matters more than trying to cover the whole matrix.

ATT&CK also doesn't prescribe defensive controls or remediation. It describes what attackers do. Turning that into a detection and prevention program still requires significant expertise and judgment.
