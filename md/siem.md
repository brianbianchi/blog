# SIEM and Log Analysis

Security events are happening constantly across every system in an organization. Authentication attempts, process launches, network connections, file modifications, privilege changes. Individually, most of them mean nothing. The challenge is correlating them across dozens or hundreds of systems, in real time, and surfacing the ones that actually matter. That's what a SIEM does.

## What a SIEM Is

SIEM stands for Security Information and Event Management. It's a centralized platform that collects logs and event data from across the environment, normalizes them into a consistent format, applies correlation rules to identify suspicious patterns, and generates alerts for the security team.

The core functions are:

- **Log aggregation**: Pull logs from endpoints, servers, firewalls, applications, cloud services, and everything else into a central store
- **Normalization**: Map vendor-specific log formats into a consistent schema so you can query across sources uniformly
- **Correlation**: Apply rules that look for patterns across multiple events and sources
- **Alerting**: Notify analysts when correlation rules fire
- **Retention**: Store logs long enough to support forensic investigations after the fact
- **Dashboards**: Give analysts visibility into what's happening across the environment

Without a SIEM, detecting an attack that spans multiple systems requires manually correlating logs from each of those systems. That's not feasible at any meaningful scale.

## Log Sources

The value of a SIEM depends entirely on the quality of the logs feeding it. The most important sources for most organizations:

**Windows Event Logs** are the primary source of endpoint and authentication telemetry in Windows environments. Security-relevant events all live in the Security channel.

**Sysmon** (System Monitor) extends Windows logging significantly. It captures events that the native Windows Security log misses entirely, including process creation with full command lines, network connections with process context, file creation, and registry modifications.

**Firewall and network logs** provide visibility into east-west and north-south traffic flows, blocked connections, and unusual communication patterns.

**Web server and proxy logs** capture HTTP requests, which is where a lot of web application attack activity shows up.

**DNS logs** are underutilized but valuable. DNS is used for C2 communication, data exfiltration (DNS tunneling), and initial access (malicious domains). If you're not logging DNS queries, you're missing a detection opportunity.

**EDR telemetry** from endpoint detection products provides rich behavioral data that complements traditional Windows event logs.

## Key Windows Event IDs

These are the events that matter most for detection. Worth memorizing or at least keeping handy.

| Event ID | Description |
|----------|-------------|
| 4624 | Successful logon. Logon type matters: Type 2 is interactive, Type 3 is network, Type 10 is RemoteInteractive (RDP). |
| 4625 | Failed logon. Multiple 4625s followed by a 4624 is a brute force pattern. |
| 4648 | Logon using explicit credentials (runas, or pass-the-hash behavior). |
| 4672 | Special privileges assigned to new logon (admin-equivalent access). |
| 4720 | User account created. |
| 4722 | User account enabled. |
| 4728 | Member added to security-enabled global group. |
| 4732 | Member added to security-enabled local group. |
| 4756 | Member added to universal security group. |
| 4776 | NTLM authentication attempt (credential validation on domain controller). |
| 4768 | Kerberos TGT requested. |
| 4769 | Kerberos service ticket requested. |
| 7045 | New service installed. Common persistence mechanism. |
| 4698 | Scheduled task created. Another common persistence mechanism. |
| 4688 | Process creation (requires audit policy to be enabled; Sysmon Event ID 1 is far richer). |
| 1102 | Audit log cleared. An attacker covering tracks. |

The logon type field in 4624 is one of those details that separates a decent analyst from a good one. Type 3 (network logon) appearing on workstations from unexpected source IPs is a classic lateral movement indicator. Type 10 (RemoteInteractive) shows RDP sessions.

## Sysmon

Sysmon is a free Microsoft Sysinternals tool that runs as a service and logs to the Applications and Services Logs channel rather than the Security channel. It captures things the default Windows audit policy simply doesn't.

Key Sysmon event IDs:

| Event ID | Description |
|----------|-------------|
| 1 | Process creation, including full command line and parent process |
| 3 | Network connection, with process context |
| 7 | Image loaded (DLL load) |
| 8 | CreateRemoteThread (process injection indicator) |
| 10 | ProcessAccess (credential dumping tools access lsass.exe with this) |
| 11 | File creation |
| 12/13/14 | Registry events (create, set, delete) |
| 15 | FileCreateStreamHash (alternate data streams) |
| 22 | DNS query |

Sysmon Event ID 1 is particularly valuable because it captures the full command line of every process. This is what lets you see `powershell.exe -EncodedCommand <base64blob>` or `cmd.exe /c whoami > C:\temp\out.txt` rather than just `powershell.exe`. The difference in detection capability is enormous. The SwiftOnSecurity Sysmon configuration is a good starting point for deployment.

## Correlation Rules

A correlation rule is a query or logic pattern that fires an alert when specific conditions are met across one or more log sources. A few common examples:

**Brute force detection**: More than 10 Event ID 4625 failures from the same source IP in five minutes, followed by a 4624 success.

**Lateral movement**: Event ID 4624 with logon type 3 on a workstation, where the source IP is another workstation (not a server or domain controller). Workstation-to-workstation authentication is unusual in most environments.

**New service installation**: Event ID 7045 outside of a known change window, or on a system that doesn't typically see service changes.

**Scheduled task creation**: Event ID 4698, especially with command lines that reference temp directories, PowerShell, or encoded commands.

**LSASS access**: Sysmon Event ID 10 where the target process is `lsass.exe` and the source is not a known legitimate tool. This is what Mimikatz and similar credential dumping tools trigger.

**Log clearing**: Event ID 1102 (Security log cleared) or 104 (System log cleared) should almost always alert.

The hard part isn't writing the rules. It's tuning them so they fire on real attacks without flooding analysts with alerts for routine administrative activity.

## Common SIEM Platforms

**Splunk** is the market leader. It has a powerful search language (SPL), excellent ecosystem of apps, and handles massive log volumes well. It's expensive, which is a real constraint for smaller organizations.

**Elastic Stack (ELK)**: Elasticsearch for storage and search, Logstash or Beats for ingestion, Kibana for visualization. Open source and free at the core, with paid features available. More operational overhead than Splunk but significantly cheaper.

**Microsoft Sentinel** is Azure's cloud-native SIEM. If you're heavily invested in Microsoft's ecosystem (Azure AD, Defender, Office 365), Sentinel integrates tightly with those sources and has reasonable pricing for existing Azure customers.

**IBM QRadar** is a longtime enterprise player, more common in large organizations and regulated industries. It has a reputation for being powerful but operationally heavy.

## Splunk Basics

If you end up working with Splunk, a few fundamentals go a long way.

Basic search structure: `index=windows EventCode=4625 | stats count by src_ip | sort -count`

Useful search patterns:

```
# Failed logon attempts by source IP
index=windows EventCode=4625 | stats count by src_ip, user | sort -count

# Successful logons after failures (brute force)
index=windows (EventCode=4625 OR EventCode=4624)
| stats count(eval(EventCode=4625)) as failures, count(eval(EventCode=4624)) as successes by src_ip
| where failures > 5 AND successes > 0

# New services installed
index=windows EventCode=7045 | table _time, host, ServiceName, ServiceFileName

# PowerShell with encoded commands (via Sysmon)
index=sysmon EventCode=1 Image="*powershell.exe*" CommandLine="*-enc*" OR CommandLine="*-EncodedCommand*"
| table _time, host, User, CommandLine

# Timechart of logon failures over time
index=windows EventCode=4625 | timechart count by host
```

The `stats`, `timechart`, `eval`, and `table` commands do most of the work in security queries. Learning those well gets you most of the way there.

## Challenges

**Alert fatigue** is the central problem in SIEM operations. A system that generates hundreds of alerts per day trains analysts to stop taking alerts seriously. Tuning signal from noise is ongoing work, not a one-time configuration.

**Log volume** can be expensive and operationally challenging. Ingesting everything from every source sounds ideal but can be cost-prohibitive and make searches slow. Decisions about what to log and retain require balancing cost against detection coverage.

**Detection gaps**: A SIEM only detects what it has rules and log sources for. If attackers operate using living-off-the-land techniques (legitimate admin tools, signed binaries), or target systems that aren't feeding logs to the SIEM, the alerts won't fire.

**Attackers who know what to clear**: Windows Event ID 1102 (Security log cleared) is itself a logged event, but only if it's ingested before the attacker terminates the connection. Clearing logs on a system before disconnecting is a real attacker technique.

## SIEM and Threat Hunting

There's an important distinction between SIEM-driven detection and threat hunting. SIEM alerts are reactive: something triggers a rule, an alert fires, an analyst investigates. Threat hunting is proactive: an analyst forms a hypothesis about attacker behavior (based on threat intelligence or ATT&CK techniques), then searches the available data to look for evidence of that behavior, without waiting for an alert to fire.

In practice, good threat hunting often leads to new detection rules. You hunt for a technique, find it, document the indicators, and turn them into a correlation rule so the next occurrence alerts automatically. The SIEM is the tooling; hunting is the practice of actively looking for what the rules haven't caught yet.
