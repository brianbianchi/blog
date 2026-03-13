# SNMP: The Forgotten Attack Surface

SNMP (Simple Network Management Protocol) is how network administrators monitor and manage devices remotely. Routers, switches, firewalls, printers, servers, UPSes, environmental sensors: if it has a network port and needs to be monitored, it probably supports SNMP. The protocol runs over UDP on port 161, with trap notifications sent to port 162.

The reason SNMP ends up on this kind of list is straightforward. It's an old protocol, it's configured once and forgotten, and the information it exposes is detailed enough to be genuinely useful to an attacker. You can pull routing tables, network interfaces, running processes, installed software, and active connections from a device without any meaningful authentication.

## SNMPv1 and SNMPv2c: Community Strings

The first two major versions of SNMP use community strings as their authentication mechanism. That's a generous word for what they actually are: plain-text passwords sent with every request, unencrypted over UDP.

There are two community strings that matter. The **read community string** controls who can query the device. The **write community string** controls who can modify settings via SNMP SET operations.

The defaults are universally known:
- Read community: `public`
- Write community: `private`

A large number of devices ship with these defaults and are deployed without changing them. It's been this way for thirty years. This isn't a subtle misconfiguration; it's essentially no authentication.

Even if you change `public` to something else, the string still travels in cleartext. Anyone on the same network segment who can see the traffic can read the community string and use it themselves. This is why SNMPv1 and v2c have no place in a security-conscious environment.

SNMPv2c added some improvements over v1 (bulk queries, better error handling) but kept the same community string authentication model. From a security standpoint, they're essentially equivalent.

## SNMPv3: Actual Security

SNMPv3 was designed to fix the authentication and confidentiality problems in the earlier versions. It introduced proper authentication using HMAC-MD5 or HMAC-SHA, and optional encryption of the payload using DES or AES. It also added access controls so you can limit what different users can read or modify.

Three security levels in SNMPv3:

| Level | Authentication | Encryption |
|-------|---------------|------------|
| `noAuthNoPriv` | None | None (same as v1/v2c) |
| `authNoPriv` | Yes (HMAC) | No |
| `authPriv` | Yes (HMAC) | Yes (AES/DES) |

`authPriv` is what you want. It's the only mode that actually protects the data in transit. If you're running SNMPv3 but only at `noAuthNoPriv`, you've gained nothing over v2c.

The reality is that SNMPv3 adoption has been slow. Network gear from five years ago often only supports v1 and v2c in a usable way. Legacy management systems don't support v3. Lazy configurations stick with what works. The result is that in most environments, v1 and v2c are still active even when v3 is also available.

## The MIB and OIDs

The MIB (Management Information Base) is the schema that defines what data a device exposes via SNMP. It's a hierarchical tree of OIDs (Object Identifiers), where each OID maps to a specific piece of information. OIDs look like `1.3.6.1.2.1.1.1.0` (the system description).

The tree is standardized in part and vendor-specific in part. The standard MIBs (under `1.3.6.1.2.1`) cover things like:

- `sysDescr` (1.3.6.1.2.1.1.1): System description, often includes OS and version
- `sysName` (1.3.6.1.2.1.1.5): Hostname
- `ifTable` (1.3.6.1.2.1.2.2): Network interfaces, their IP addresses, traffic counters
- `ipRouteTable` (1.3.6.1.2.1.4.21): Routing table
- `hrSWRunTable` (1.3.6.1.2.1.25.4.2): Running processes
- `hrSWInstalledTable` (1.3.6.1.2.1.25.6.3): Installed software
- `hrDeviceTable` (1.3.6.1.2.1.25.3.2): Attached devices

Vendor-specific MIBs extend this. Cisco has its own subtree. HP has another. These can expose device-specific configurations, credentials stored in configuration files, VPN tunnel details, and more.

The key point is that with read access to a device's SNMP, you can extract a detailed inventory of that device's configuration and state.

## Tools

### snmpwalk

`snmpwalk` traverses the MIB tree starting from a given OID and prints everything below it. Starting from the root of the tree gives you everything the device is willing to share.

```
# Walk everything (v2c with "public" community)
snmpwalk -v2c -c public 192.168.1.1

# Walk from a specific OID
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.1

# Walk system information only
snmpwalk -v2c -c public 192.168.1.1 system

# Use v3 with authentication
snmpwalk -v3 -l authPriv -u username -a SHA -A authpassword -x AES -X privpassword 192.168.1.1
```

The output can be enormous. Piping to a file and then grepping is the practical approach.

### snmpget

`snmpget` retrieves a specific OID rather than walking the whole tree. Useful when you know exactly what you're looking for.

```
# Get system description
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.1.0

# Get hostname
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.5.0
```

### onesixtyone

When you don't know the community string, `onesixtyone` brute-forces it. It's fast because SNMP runs over UDP and onesixtyone can send many requests in parallel.

```
# Try common community strings against a single host
onesixtyone -c /usr/share/doc/onesixtyone/dict.txt 192.168.1.1

# Scan a range
onesixtyone -c community_strings.txt -i ip_list.txt
```

A basic wordlist should include `public`, `private`, `community`, `manager`, the organization's name, and common variations. Many people pick a "clever" community string like the company name, which shows up in the first dozen entries of any reasonable wordlist.

### snmp-check

`snmp-check` is a convenience tool that formats SNMP output in a more readable way, automatically pulling commonly useful information: system info, users, network interfaces, routing table, processes, and more.

```
snmp-check 192.168.1.1
snmp-check -c private 192.168.1.1 -v 2c
```

It's a good first pass when you've confirmed a community string works and want a quick overview without having to navigate raw OID output.

## What Attackers Look For

**Community strings set to "public" or "private"** are the first check. If a device hasn't changed its defaults, that's immediately exploitable.

**Write access via the write community string** is a significant escalation. With SNMP write access, you can modify device configuration. On a router, that means changing routing tables, disabling interfaces, or altering NAT rules. Some devices allow you to write new configuration files via SNMP TFTP operations, which can include replacing the entire running config.

**Network topology from routing tables and ARP cache** is useful for mapping an environment you didn't previously understand. A router's routing table tells you what subnets exist and how they're connected.

**Running processes and installed software** from `hrSWRunTable` and `hrSWInstalledTable` give you an inventory of what's running on a server without needing any access to the server itself.

**Usernames in process names** occasionally show up. Processes like `sudo -u dbadmin` or personal cron jobs can leak account names.

**Network device credentials in extended MIBs** are the jackpot. Some devices expose configuration data including passwords in plaintext through vendor-specific OIDs. This is rarer on modern firmware but common on older gear.

## Why It Gets Forgotten

SNMP occupies a weird corner of most network security programs. It's not a web service, so it doesn't get caught in web application scans. It's UDP, so basic TCP port scans miss it unless you explicitly scan UDP. It runs on network gear rather than servers, so it sits outside the normal patch and configuration management processes. The people who configure it are often network engineers, not security people.

The combination of those factors means SNMP frequently gets left with default community strings, enabled on devices that don't need it, and never reviewed. It's the kind of thing you find in a penetration test and the client has genuinely never thought about it.

During external assessments, look for SNMP on exposed network devices and printers. During internal assessments, scan the entire subnet for UDP port 161 and try `public` against everything that responds. The hit rate is higher than you'd hope.

```
# Quick check across a subnet
nmap -sU -p 161 192.168.1.0/24 --open
onesixtyone -c community.txt 192.168.1.0/24
```

The fact that it's boring and old is precisely the reason it doesn't get fixed.
