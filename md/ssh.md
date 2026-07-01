# SSH

SSH (Secure Shell) is how you talk to a remote machine without someone in the middle being able to read or tamper with the conversation. It's encrypted, authenticated, and runs over TCP port 22. Most of the time you're using it to get a shell on a server — but it also does port forwarding, file transfers, and tunneling through firewalls.

## How Authentication Works

Password auth is simple: you type a password, the server checks it. Public key auth is better.

You generate a **key pair** — a private key you keep and a public key you share. The server stores your public key in `~/.ssh/authorized_keys`. When you connect:

1. Server sends a random challenge encrypted with your public key
2. Only your private key can decrypt it
3. Your client decrypts and sends back a signed response
4. Server verifies the signature — if it checks out, you're in

Your private key never leaves your machine. That's the point.

## Generating Keys

```bash
ssh-keygen -t ed25519 -C "your@email.com"
```

| Flag | What it does |
| ---- | ------------ |
| `-t` | Key type |
| `-C` | Comment (shows up in `authorized_keys`) |
| `-f` | Output filename |
| `-b` | Key size (RSA only) |

**Ed25519** is the default choice — small, fast, and secure. Use RSA 4096 only if you need to interop with something old.

Keys land in `~/.ssh/` by default:

| File | What it is |
| ---- | ---------- |
| `id_ed25519` | Private key — never share this |
| `id_ed25519.pub` | Public key — safe to share |
| `authorized_keys` | Public keys allowed to log in (server-side) |
| `known_hosts` | Fingerprints of servers you've connected to |
| `config` | Per-host connection settings |

Add your public key to a server:

```bash
ssh-copy-id user@host          # copies ~/.ssh/id_*.pub
ssh-copy-id -i ~/.ssh/key.pub user@host   # specific key
```

Or manually append the public key to `~/.ssh/authorized_keys` on the server.

## The Config File

`~/.ssh/config` is one of the most underused tools in SSH. It lets you define aliases and defaults so you're not typing out flags every connection.

```
Host myserver
    HostName 203.0.113.42
    User deploy
    Port 2222
    IdentityFile ~/.ssh/id_ed25519

Host bastion
    HostName bastion.example.com
    User admin

Host internal
    HostName 10.0.1.5
    User ubuntu
    ProxyJump bastion
```

With that config, `ssh myserver` is all you need.

| Directive | What it does |
| --------- | ------------ |
| `HostName` | Actual address or IP |
| `User` | Login username |
| `Port` | Port (default 22) |
| `IdentityFile` | Which private key to use |
| `ProxyJump` | Hop through another host first |
| `ForwardAgent` | Forward your local SSH agent through the connection |
| `ServerAliveInterval` | Keepalive ping interval in seconds |
| `StrictHostKeyChecking` | Whether to reject unknown hosts |

`Host *` at the top acts as a fallback for any host not matched above.

## SSH Agent

The agent holds your decrypted private keys in memory so you don't retype your passphrase on every connection.

```bash
eval "$(ssh-agent -s)"    # start the agent
ssh-add ~/.ssh/id_ed25519  # add a key
ssh-add -l                 # list loaded keys
ssh-add -d ~/.ssh/id_ed25519  # remove a key
```

macOS Keychain integrates with ssh-agent automatically. Add to your config to persist keys across reboots:

```
Host *
    AddKeysToAgent yes
    UseKeychain yes
```

**Agent forwarding** (`ForwardAgent yes` or `-A` flag) lets a remote server use your local agent to make further SSH connections — useful when jumping through a bastion. Be careful: a compromised remote host can use your agent while it's forwarded.

## Common Commands

```bash
# Basic connection
ssh user@host
ssh -p 2222 user@host              # custom port

# Run a command without opening a shell
ssh user@host "df -h"

# Copy files
scp file.txt user@host:~/          # local → remote
scp user@host:~/file.txt .         # remote → local
scp -r dir/ user@host:~/           # recursive

# rsync (better for large/incremental transfers)
rsync -avz dir/ user@host:~/dir/
```

## Port Forwarding

SSH can forward TCP traffic through the encrypted tunnel.

**Local forwarding** — access a remote service as if it were local:

```bash
ssh -L 8080:localhost:3000 user@host
# http://localhost:8080 now hits the remote's port 3000
```

**Remote forwarding** — expose a local service on the remote server:

```bash
ssh -R 9090:localhost:3000 user@host
# remote's port 9090 now hits your local port 3000
```

**Dynamic forwarding** — SOCKS5 proxy through the remote:

```bash
ssh -D 1080 user@host
# route traffic through the proxy at localhost:1080
```

| Flag | Type | Direction |
| ---- | ---- | --------- |
| `-L local:remote` | Local | Your machine → remote |
| `-R remote:local` | Remote | Remote machine → you |
| `-D port` | Dynamic | SOCKS5 proxy |
| `-N` | — | No command, just forward |
| `-f` | — | Background the process |

## Hardening the Server

Default SSH config is fine for getting started, terrible for production. Edit `/etc/ssh/sshd_config`:

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
AllowUsers deploy ubuntu
Port 2222
MaxAuthTries 3
```

Restart after changes: `sudo systemctl restart sshd`

**fail2ban** bans IPs after repeated failed attempts. Worth running on anything internet-facing.

## Checking and Trusting Hosts

First time you connect to a host, SSH shows its fingerprint and asks you to verify:

```
The authenticity of host '203.0.113.42' can't be established.
ED25519 key fingerprint is SHA256:abc123...
Are you sure you want to continue connecting?
```

Say yes and it's added to `~/.ssh/known_hosts`. If the fingerprint changes on a future connection (server reinstalled, or someone is doing a MITM), SSH refuses with a loud warning. Check it:

```bash
ssh-keyscan host 2>/dev/null | ssh-keygen -lf -   # get host fingerprint
ssh-keygen -R host                                 # remove old entry from known_hosts
```
