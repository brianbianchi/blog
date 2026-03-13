# How Firewalls and IDS/IPS Work

A firewall is not one thing. The word covers at least three distinct generations of technology, each with a different threat model and a different set of limitations. Understanding those differences matters because selecting the wrong tool, or misunderstanding what a tool actually does, is how you end up with a false sense of security.

## Packet Filtering

The original firewall operates at layers 3 and 4 of the OSI model. It looks at each packet in isolation: source IP, destination IP, protocol (TCP/UDP/ICMP), source port, destination port. Based on those fields, it either passes or drops the packet.

This is stateless. The firewall has no memory of previous packets. Every packet is evaluated independently. That simplicity is also a limitation: a packet with the right header fields will pass regardless of whether it belongs to a legitimate conversation.

Packet filtering is still everywhere. ACLs on routers are packet filters. `iptables` rules that match on port and protocol without tracking state are packet filters. Fast and simple, but easy to evade if you know the rules.

## Stateful Inspection

Stateful firewalls track the state of TCP connections. When a SYN arrives and is permitted, the firewall records that session in a state table: source IP, destination IP, source port, destination port, and current TCP state. Subsequent packets in that conversation are matched against the table; if they fit, they pass without re-evaluating the full ruleset.

This matters for a couple of reasons. It blocks packets that look like responses to conversations that never happened. An attacker can't craft a bare ACK packet and get it through because the firewall won't find a matching entry in its state table. It also helps against TCP SYN flood attacks, which attempt to exhaust server resources by sending SYNs without completing the handshake. A stateful firewall can limit half-open connections to prevent that table from being exhausted.

The state table itself is an attack surface. Sending enough unique SYN packets can overflow the table and cause connection drops or degrade performance. That's why stateful firewalls pair connection tracking with limits on half-open connection counts.

## Application Layer and Next-Generation Firewalls

Application-layer firewalls operate at layer 7. They understand the actual protocols flowing through them: HTTP, DNS, SMTP, TLS. Instead of asking "is this TCP port 80?" they ask "is this actually valid HTTP? Does this request match an attack signature?"

Next-generation firewalls (NGFWs) extend this further. Deep packet inspection (DPI) lets them identify applications regardless of port. Dropbox on port 443 looks different from a banking HTTPS session if you inspect the TLS handshake and application behavior carefully enough. NGFWs typically bundle IPS, SSL/TLS inspection, application identification, and user identity awareness into a single platform. Palo Alto Networks built their reputation on this model. Fortinet's FortiGate competes on price-performance and is common in mid-market environments.

The catch with TLS inspection is that it's a man-in-the-middle by design. The firewall terminates the TLS session, inspects the plaintext, re-encrypts, and forwards it on. This requires deploying a CA certificate to all client devices and has its own privacy and operational overhead.

## Firewall Rules and Policies

Rules are evaluated in order. The first matching rule wins. This is important because rule ordering mistakes are a common source of security gaps.

**Default deny** means the policy blocks everything not explicitly permitted. This is the correct security posture. **Default allow** exists in environments where someone prioritized convenience heavily enough to undermine the whole point of having a firewall.

Inbound rules control traffic entering a network or host. Outbound rules control traffic leaving. Many organizations focus heavily on inbound and give outbound little attention, which is a mistake. Attackers already inside the network need outbound connectivity for command and control and data exfiltration. Egress filtering catches a lot of that activity.

## Network vs Host-Based Firewalls

A network firewall sits at a boundary and protects many systems. A host-based firewall runs on the individual machine and controls what that specific host can send and receive.

On Linux, `iptables` and its successor `nftables` are the standard host-based firewall tools. `iptables` is still heavily documented and used, but `nftables` is the direction things are heading. On Windows, Windows Defender Firewall serves the same role and can be managed centrally via Group Policy.

Host-based firewalls matter specifically for lateral movement. Even if an attacker gets past the network perimeter, host firewalls that restrict which internal hosts can talk to each other limit where the attacker can go next.

## IDS vs IPS

An intrusion detection system observes traffic and raises alerts. It does not block anything. An intrusion prevention system sits inline in the traffic path and can drop or modify packets in real time.

The placement difference is significant. An IDS is typically connected to a **SPAN port** (also called a mirror port) on a switch. The switch copies all traffic to the SPAN port, and the IDS sees it passively. Because the IDS is out-of-band, it has zero impact on traffic flow. It also can't block anything; by the time an alert fires, the packet has already been delivered.

An IPS is inline: traffic physically flows through it. This lets it drop malicious packets before they reach the destination, but it also means the device is a single point of failure. A crashing IPS takes down the network path unless there's a hardware failopen mechanism that passes traffic through when the device goes down.

The trade-off is real. IDS is safer to deploy but you're watching the attack happen. IPS can stop attacks but false positives block legitimate traffic, and the device itself becomes an availability dependency.

## Detection Methods

### Signature-Based

Signature detection compares traffic against a database of known attack patterns. A Snort rule might match on a specific byte sequence present in a known exploit. It's fast, reliable for known threats, and generates few false positives.

The limitation is obvious: it only catches what it knows about. Zero-days and novel techniques have no signature. Attackers who know which signatures are deployed can sometimes modify their payloads to avoid matching while preserving functionality.

### Anomaly-Based

Anomaly detection builds a model of normal traffic and alerts on deviations. This can theoretically catch new attacks because it doesn't need a signature, just a behavior that diverges from baseline.

In practice, anomaly detection is difficult to tune. Baselines shift legitimately (a new application deployment, a software update, seasonal traffic patterns), and the false positive rate can be high. Most production deployments require significant tuning time before anomaly-based alerts are actually actionable.

### Hybrid

Most modern IDS/IPS platforms combine both approaches. Signatures handle known-bad traffic efficiently. Anomaly detection supplements with statistical and behavioral analysis. Each method covers the other's blind spots.

## Evasion Techniques

**Fragmentation**: Splitting a malicious payload across multiple IP fragments can defeat a naive IDS that inspects packets individually. A proper IDS reassembles fragments before inspection, but not all implementations do this correctly for every protocol.

**Protocol anomalies**: Sending technically malformed but functional packets can confuse IDS parsing logic. Different operating systems handle edge cases differently, and an attacker who understands how both the IDS and the target interpret ambiguous packets can craft traffic that the IDS sees as benign but the target treats as an attack.

**Encryption**: An IDS cannot inspect encrypted traffic without decrypting it first. TLS-wrapped malicious traffic looks like ordinary HTTPS unless the IDS is doing SSL/TLS inspection. This is one reason network-based detection has become harder as TLS adoption has become nearly universal.

**Slow scans**: A port scan that sends one probe per hour across a /24 may never exceed any threshold that triggers an alert. Speed-based detection requires the attacker to be impatient.

## Common Products

**Snort** is the original open source IDS/IPS, now maintained by Cisco. It has a large rule ecosystem and strong community support. **Suricata** is the modern open source alternative; it's multithreaded (Snort 2 was single-threaded, which became a bottleneck at higher traffic volumes), supports the Snort rule format, and handles significantly higher throughputs. Both can run in passive IDS mode or inline IPS mode.

On the commercial side, **Palo Alto Networks** NGFWs are widely considered the enterprise standard. **Fortinet FortiGate** is a strong competitor, particularly in the mid-market, and bundles IPS, application identification, URL filtering, and sandboxing into the same platform.

## Web Application Firewalls

A WAF is a layer 7 device that specifically understands HTTP and HTTPS. It sits in front of web applications and inspects requests and responses for attack patterns: SQL injection, XSS, path traversal, local file inclusion, and similar web-specific attacks.

The **OWASP Core Rule Set (CRS)** is the most widely deployed WAF ruleset. It covers the OWASP Top 10 and is used by ModSecurity (the classic open source WAF engine), AWS WAF, and many commercial products.

WAF bypass is its own discipline. Common techniques include encoding tricks (URL encoding, double encoding, Unicode normalization), case variation (`SeLeCt` instead of `SELECT`), inserting comments to break up SQL keywords (`SE/**/LECT`), and splitting payloads across multiple parameters or headers. A WAF adds a useful layer of defense but is not a substitute for fixing the underlying vulnerability in the application.

## Placement and Architecture

The classic pattern uses a **DMZ**: a network segment sitting between two firewalls (or two interfaces on the same firewall). Public-facing servers (web servers, mail relays, VPN concentrators) go in the DMZ. They're accessible from the internet but isolated from the internal network. If a DMZ host is compromised, the attacker faces another firewall before reaching internal systems.

Layered defense means no single control is the last line. The perimeter firewall filters at the boundary. The WAF protects web applications specifically. Host-based firewalls limit exposure on individual servers. The IPS watches for known attack patterns. None of these individually stops everything, but each layer requires an attacker to do more and creates more opportunities for detection.

```
Internet --> [Perimeter Firewall] --> [DMZ: web/mail/VPN] --> [Internal Firewall] --> [Internal Network]
                                               |
                                           [IDS/IPS]
```

The assumption that a single firewall at the network edge constitutes adequate security is long outdated. Modern architectures are built on the premise that attackers will eventually get inside, and layer controls accordingly.
