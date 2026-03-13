# Network Segmentation and Zero Trust

The oldest and still most common network security failure is a flat network. Everything on the same subnet, or all subnets able to reach each other freely. When an attacker compromises one system on a flat network, they can typically reach every other system without crossing any additional controls. One phished email becomes access to every server, every database, every file share. Segmentation is the architectural answer to this problem.

## The Flat Network Problem

A flat network treats perimeter security as the only security. The implicit assumption is that if traffic got inside, it's trustworthy. This model was marginal when office networks were genuinely isolated from the internet. It's indefensible now.

Attackers who gain a foothold via phishing, a compromised VPN credential, or a vulnerable public-facing application then perform lateral movement: moving from the initial beachhead to other systems, looking for credentials, privileged access, and valuable data. On a flat network, nothing stops this. The attacker pivots freely.

## Network Segmentation

Segmentation divides a network into zones with controlled communication between them. The primary implementation mechanism in enterprise networks is VLANs.

A VLAN (Virtual LAN) is a logical network boundary enforced at the switch level. Systems on VLAN 10 and systems on VLAN 20 cannot communicate directly; their traffic must pass through a router or firewall at the VLAN boundary. By putting the firewall in that path, you control which inter-VLAN communication is permitted.

Common segmentation zones:

| Zone | Purpose | Notes |
|------|---------|-------|
| User VLAN | Employee workstations | Should not have direct access to server or management VLANs |
| Server VLAN | Internal application and file servers | Restrict access to specific ports and protocols |
| DMZ | Public-facing systems: web servers, mail relays, VPN concentrators | Accessible from internet but isolated from internal network |
| Management VLAN | Network devices, out-of-band management | Very restricted; admin access only |
| OT/IoT VLAN | Operational technology, printers, cameras, industrial systems | Often have unpatched firmware; isolate them |
| Guest VLAN | Visitor wireless | Internet access only; no internal access |

The management VLAN is frequently overlooked. Network devices (switches, routers, firewalls) have management interfaces that should be on a dedicated VLAN accessible only from admin jump hosts, not from general user subnets.

## The DMZ

The DMZ (demilitarized zone) is a network segment specifically for systems that need to be accessible from the internet while being protected from the internal network. The classic implementation uses two firewalls or a firewall with three interfaces: one facing the internet, one in the DMZ, and one facing the internal network.

Systems that belong in a DMZ: web servers and load balancers, mail relay servers (which receive inbound email from the internet), VPN concentrators, publicly accessible APIs. Systems that don't belong there: databases, domain controllers, internal application servers, anything containing sensitive data that doesn't need to be directly reachable from outside.

The key property of a DMZ: even if an attacker fully compromises a DMZ host, they still face the internal firewall before reaching the internal network. The compromise is contained.

## Microsegmentation

Traditional VLANs create network zones but don't address traffic within a zone. On a server VLAN, an attacker who compromises one server can still reach every other server on the same VLAN. Microsegmentation takes segmentation further, enforcing controls at the individual host level.

Microsegmentation typically uses software-defined networking (SDN) or host-based policies to restrict which specific hosts can communicate with which other hosts, on which ports, using which protocols. The goal is least-privilege networking: a web server should be able to talk to its specific database on its specific port, and nothing else.

The challenge is operational complexity. Defining and maintaining host-level network policies across hundreds or thousands of servers requires automation and a good understanding of application communication patterns. Organizations often start with coarse-grained segmentation and work toward microsegmentation over time.

## Zero Trust: The Philosophy

Zero Trust is an architectural model, not a product. The core idea: don't trust anything by default, regardless of network location. Traditionally, being inside the network perimeter granted implicit trust. Zero Trust eliminates that assumption.

The three core principles, as articulated by NIST SP 800-207:

**Verify explicitly**: Every access request must be authenticated and authorized based on all available data points: identity, device health, location, service being accessed, data classification. No implicit trust.

**Use least privilege**: Access is granted for the minimum time and scope needed. No standing privileged access. Just-in-time access where possible.

**Assume breach**: Design as if an attacker may already be inside. Microsegment everything. Encrypt internal traffic. Monitor everything. Limit blast radius.

## Zero Trust vs Perimeter Security

Traditional perimeter security is sometimes described as a "hard shell, soft inside" model. Strong controls at the edge (firewall, IDS, VPN), but once inside, relatively free movement. The perimeter assumption was that insiders are trusted and outsiders are not.

This model breaks down for several reasons. Remote work means users aren't always inside the perimeter. Cloud services mean data isn't always inside the perimeter. Attackers who breach the perimeter gain the same implicit trust as legitimate insiders. Supply chain compromises (SolarWinds, the MOVEit exploitation) demonstrated how adversaries can enter environments through trusted software.

Zero Trust doesn't eliminate perimeter controls; it stops treating them as sufficient. Every access request is evaluated on its merits regardless of where it originates.

## Identity as the New Perimeter

In a Zero Trust architecture, identity replaces network location as the primary trust signal. The question is no longer "is this request coming from inside our network?" but "who is making this request, from what device, in what context, and is that combination legitimate for this resource?"

This means the identity provider becomes critical infrastructure. Azure AD, Okta, Ping, or similar platforms become the centralized control point for access decisions. Conditional access policies can require that a device be enrolled in MDM, have up-to-date security patches, and not be flagged by endpoint detection before allowing access to sensitive resources.

## Components of a Zero Trust Architecture

A real Zero Trust implementation touches many systems:

**Identity provider (IdP)**: Centralizes authentication. Single sign-on with strong MFA everywhere. All applications federate to it.

**Device management**: MDM (Mobile Device Management) or EMM platforms that enforce device compliance: encryption required, OS patching, EDR installed. Devices that fail compliance are denied access regardless of the user's credentials.

**Conditional access**: Policies that evaluate access requests against context and apply appropriate controls. Accessing email from a managed device on a corporate network gets a different treatment than accessing it from an unknown device in an unusual location.

**Microsegmentation**: Network-level enforcement of least-privilege communication between workloads.

**Continuous monitoring**: Log everything. Behavioral analytics to detect anomalies in access patterns. The assumption-of-breach principle requires that if something is wrong, you can detect it.

## Getting There in Practice

Zero Trust is often described as a destination, but it's more accurate to call it a direction. Most organizations aren't going to redesign their entire network and application architecture at once.

Practical starting points that provide immediate value:

**MFA everywhere**: The single highest-return investment. Credential-based attacks (phishing, password spray, credential stuffing) are the most common initial access vector. MFA breaks most of them.

**Device compliance checks**: Before you enforce microsegmentation on every workload, enforce that managed devices meet a health baseline before accessing sensitive resources.

**Remove standing privileged access**: Administrators shouldn't have persistent admin accounts that are active all the time. Use privileged access workstations and just-in-time privilege elevation. This limits the damage from compromised admin credentials.

**Log all access**: You can't enforce Zero Trust principles consistently if you can't see what's happening. Centralize authentication and access logs.

**Segment the most sensitive assets first**: You don't have to microsegment everything at once. Start with crown jewel systems: domain controllers, production databases, code repositories, financial systems.

Zero Trust is an ongoing process. The organizations that treat it as a product to buy and deploy miss the point. It's a philosophy that influences how you make architectural decisions over time.
