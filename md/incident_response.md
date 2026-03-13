# Incident Response: What Actually Happens

The uncomfortable truth about security is that breaches happen. Even well-defended organizations get compromised. The question is never only "can we prevent every attack?" but also "when something gets through, how do we limit the damage, understand what happened, and make sure it doesn't happen the same way again?" That's incident response.

## Why IR Matters

Detection capability and response capability are separate things. An organization can have excellent logging, good alerting, and a team of skilled analysts, and still handle incidents poorly because nobody has defined what to do when an alert turns into a confirmed incident. Improvising under pressure, with stakeholders demanding answers and attackers potentially still active in the environment, produces bad outcomes. Preparation is what separates a contained incident from a catastrophe.

## The IR Lifecycle

Two frameworks dominate incident response planning. They cover the same ground with different structures.

**PICERL** is the six-phase model common in security certifications and many IR programs:

1. **Preparation**: Build the capability before you need it
2. **Identification**: Determine that an incident is actually occurring
3. **Containment**: Stop the bleeding
4. **Eradication**: Remove the threat
5. **Recovery**: Restore operations safely
6. **Lessons Learned**: Figure out what to do differently

**NIST SP 800-61** condenses this into four phases: Preparation; Detection and Analysis; Containment, Eradication, and Recovery; Post-Incident Activity. The content is essentially the same.

Neither model is prescriptive about the specific steps because incidents vary enormously. A ransomware outbreak looks nothing like a targeted espionage intrusion. The lifecycle gives you a framework; the playbooks give you the specifics.

## Preparation

Preparation is the phase that determines how every other phase goes. Organizations that skip preparation discover this under the worst possible circumstances.

**IR plan**: A documented policy that defines what constitutes an incident, who has authority to make decisions, how communications flow internally and externally, and what the process looks like at each phase. It should be reviewed and approved by leadership, not just the security team.

**Playbooks**: Step-by-step procedures for specific incident types. Ransomware playbook, phishing playbook, insider threat playbook, compromised credential playbook. Each covers the specific triage steps, containment actions, evidence to collect, and escalation paths for that scenario.

**Tabletop exercises**: Simulate an incident scenario with the relevant stakeholders (not just security, but also legal, communications, executives, IT operations) to walk through the plan and find gaps before a real incident does it for you.

**Tooling**: Forensic workstations with imaging software, hardware write blockers, memory capture tools, a log aggregation solution, and a ticketing or case management system for tracking the investigation. Some organizations maintain an "IR jump bag" with hardware ready to deploy.

**External IR firm retainer**: Having a contractual relationship with an IR firm before you need them means you're not negotiating a contract while an attacker is active in your environment. The retainer also often includes access to their threat intelligence and tooling.

**Communication trees**: Who gets called at 2am? Who approves containment actions that will affect production? Who is authorized to communicate with law enforcement or notify regulators?

## Identification

An incident can be triggered by many things: a SIEM alert, a user reporting something suspicious, a threat intelligence tip, an alert from an EDR platform, or notification from an external party (law enforcement, a security researcher, a business partner).

Initial triage has two goals: determine whether a real incident is occurring (versus a false positive, a misconfiguration, or a policy violation that isn't an active attack), and get a rough sense of scope and severity.

Severity classification drives the response. A single compromised user account on a non-critical system warrants a different response than an attacker with domain admin access in a hospital network. Most organizations define severity tiers and prescribe escalation paths for each.

The people who need to know in the first hour typically include: the security team lead, IT operations (they'll be needed for containment), and legal. Legal involvement early protects attorney-client privilege over the investigation findings, which matters if litigation or regulatory action follows.

## Containment

Containment stops the attack from spreading or doing more damage. There are two modes, and they often run in parallel.

**Short-term containment** is immediate action: isolate the compromised host from the network, kill a malicious process, block an attacker's IP at the firewall, disable a compromised account, revoke a stolen API key. The goal is to stop active damage now.

**Long-term containment** is the more deliberate work: rebuilding compromised systems, patching the exploited vulnerability, rotating all affected credentials, removing malicious persistence mechanisms.

The tension in containment is between acting fast and preserving evidence. Pulling a machine's network cable immediately stops an active exfiltration, but it also potentially destroys volatile evidence: active network connections, running processes, contents of memory. The right balance depends on the situation. If the attacker is actively exfiltrating gigabytes of data, you pull the cable. If they appear to be sitting idle on a system, capturing memory before isolation may be worthwhile.

Another tension: acting too visibly can tip off the attacker. If you block a C2 IP, the attacker may notice and switch to a different communication channel, delete evidence, or pivot to a deeper position in the network. Sometimes a brief period of observation is valuable before containment, but this is a judgment call that requires experience and clear authorization.

## Eradication

Eradication is the work of actually removing the threat from the environment. This sounds simpler than it is.

The mistake most often made here: you find and remove the initial access vector, declare victory, and miss a second or third foothold the attacker established. Sophisticated attackers routinely establish multiple persistence mechanisms, across multiple systems, specifically to survive an incomplete remediation. Finding all of them requires a thorough investigation, not just removing what triggered the initial alert.

Common persistence mechanisms to check: scheduled tasks, services, registry run keys, startup folders, WMI subscriptions, modified user accounts, added local admin accounts, SSH authorized_keys, web shells on internet-facing systems, and implants in software supply chains.

## Recovery

Recovery is restoring systems to a known-good state and returning operations to normal. This means restoring from clean backups, not from the compromised state.

Before putting recovered systems back into production, verify integrity. Confirm that the restore came from a backup that predates the compromise. Scan for malware. Confirm that the vulnerability that was exploited has been patched. Monitor closely after return to production; re-infection in the first days after recovery is a real occurrence.

Recovery timelines vary from hours to weeks depending on the scope of the incident and the state of the organization's backup infrastructure. Organizations that have never tested their backups sometimes discover during recovery that the backups don't actually work. That's a bad time to find out.

## Lessons Learned

Within a week or two of closing the incident, the team should conduct a lessons-learned review. The goal is a blameless post-mortem: understanding what happened and what to do differently, not finding someone to blame.

The review should produce a timeline of the incident (attacker activity from initial access to detection), an assessment of what detection controls existed and why they didn't catch the attack sooner, and a list of concrete improvements with owners and deadlines.

Common outputs: new or tuned SIEM detection rules, patching process improvements, credential hygiene work, network segmentation changes, updated playbooks, additional training.

The lessons-learned phase is the part of the lifecycle that has the highest long-term return on investment. Organizations that do it well get measurably better at detection and response over time.

## Evidence Handling

Evidence collected during an incident may be needed months or years later, for litigation, regulatory proceedings, or insurance claims. How you handle it matters.

**Chain of custody**: Document who collected what, when, from where, and who has handled it since. This is what allows evidence to be used in legal proceedings.

**Disk imaging**: Take forensic images using a hardware write blocker so the original media is never modified. The image, not the original, is what you analyze.

**Memory capture**: Tools like WinPmem or DumpIt capture RAM before a system is powered down. Memory contains running processes, network connections, encryption keys, credentials cached in memory, and other volatile evidence that disappears at shutdown.

**Log preservation**: Export and preserve raw logs from affected systems and the SIEM before they roll out of retention windows.

Document everything. Write down the commands you ran, the timestamps, the artifacts you collected, and your observations. Notes taken in the moment are more reliable than reconstructions made days later.

## Legal and Regulatory Considerations

Most jurisdictions have breach notification laws. The specifics vary: notification timelines range from 72 hours (GDPR) to "without unreasonable delay" (many US state laws) to specific windows defined by sector regulations (HIPAA, PCI DSS). Know what applies to your organization before you're in an incident.

Law enforcement involvement is a decision that requires legal counsel. Involving law enforcement can complicate the investigation timeline and, in some jurisdictions, create disclosure obligations. It may also provide access to intelligence or investigative resources you don't have. There is no universal right answer.

Cyber insurance policies often have notification requirements and may require using specific IR firms. Read your policy before you have an incident.

## Common Mistakes

**Containing too fast without observation**: Immediately blocking an attacker's access before understanding scope can tip them off and destroy evidence. A brief period of monitored observation is sometimes the right call.

**Not containing fast enough**: The opposite problem. Watching an attacker exfiltrate data or move laterally for days because the team wanted more information is also a real failure mode.

**Assuming eradication is complete**: Finding one backdoor doesn't mean you found all of them. Thorough is not optional.

**Not preserving evidence**: Rebooting a compromised system before capturing memory, or reimaging it before taking a forensic image, destroys evidence permanently.

**Keeping it too quiet internally**: IR teams sometimes try to handle incidents entirely within the security team to avoid panic. This backfires when decisions about containment or recovery require authority that the security team doesn't have, or when stakeholders who needed to know weren't informed and find out later.

**Skipping the lessons-learned phase**: Every incident that isn't reviewed is a missed opportunity to improve. Under time pressure, the post-mortem is often the first thing dropped. This is how organizations keep having the same incidents.
