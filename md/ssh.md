# Understanding ~/.ssh

SSH (Secure Shell) is one way to talk to a remote machine. It's encrypted, authenticated, and runs over TCP port 22. Most of the time, it's used to get a shell on a server, but it's also used for port forwarding, file transfers, and tunneling through firewalls.

## How Authentication Works

Password authentication is straightforward. The user enters a password, and the server checks it against its records. It works, but it is the weaker of the two common methods.

Public key authentication uses a **key pair** instead: a private key that stays on the local machine, and a public key that is distributed to servers. Once the public key is placed in a server's `~/.ssh/authorized_keys`, the connection proceeds as follows:

1. The server sends a random challenge encrypted with the public key.
2. Only the corresponding private key can decrypt it.
3. The client decrypts the challenge and returns a signed response.
4. The server verifies the signature and grants access if it matches.

The private key never has to leave the local machine for this exchange to succeed, which is the core reason public key authentication is considered more secure than a password.

## Generating Keys

```bash
ssh-keygen -t ed25519 -C "your@email.com"
```

| Flag | What it does                            |
| ---- | --------------------------------------- |
| `-t` | Key type                                |
| `-C` | Comment (shows up in `authorized_keys`) |
| `-f` | Output filename                         |
| `-b` | Key size (RSA only)                     |

Ed25519 is the recommended default. It produces smaller keys, performs faster than RSA, and offers comparable security. RSA at 4096 bits is mainly relevant for interoperating with older systems that do not support Ed25519.

By default, keys are stored in `~/.ssh/`:

| File              | What it is                                      |
| ----------------- | ----------------------------------------------- |
| `id_ed25519`      | Private key. Never share this.                  |
| `id_ed25519.pub`  | Public key. Safe to share.                      |
| `authorized_keys` | Public keys allowed to log in (server-side)     |
| `known_hosts`     | Fingerprints of servers previously connected to |
| `config`          | Per-host connection settings                    |

To copy a key to a server:

```bash
ssh-copy-id user@host                      # copies ~/.ssh/id_*.pub
ssh-copy-id -i ~/.ssh/key.pub user@host    # specific key
```

Alternatively, the public key can be appended manually to `~/.ssh/authorized_keys` on the server.

## The Config File

`~/.ssh/config` is frequently overlooked. It allows connection details to be saved under a short alias, removing the need to repeat the same flags on every connection.

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

With this configuration in place, `ssh myserver` is sufficient to connect.

| Directive               | What it does                                       |
| ----------------------- | -------------------------------------------------- |
| `HostName`              | Actual address or IP                               |
| `User`                  | Login username                                     |
| `Port`                  | Port (default 22)                                  |
| `IdentityFile`          | Which private key to use                           |
| `ProxyJump`             | Hop through another host first                     |
| `ForwardAgent`          | Forward the local SSH agent through the connection |
| `ServerAliveInterval`   | Keepalive ping interval in seconds                 |
| `StrictHostKeyChecking` | Whether to reject unknown hosts                    |

A `Host *` block at the top of the file serves as a fallback for any host not matched by a more specific entry.

## SSH Agent

The agent holds decrypted private keys in memory so a passphrase does not need to be entered on every connection.

```bash
eval "$(ssh-agent -s)"        # start the agent
ssh-add ~/.ssh/id_ed25519     # add a key
ssh-add -l                    # list loaded keys
ssh-add -d ~/.ssh/id_ed25519  # remove a key
```

On macOS, Keychain integrates with ssh-agent automatically. Adding the following to the config file allows keys to persist across reboots:

```
Host *
    AddKeysToAgent yes
    UseKeychain yes
```

**Agent forwarding** (`ForwardAgent yes`, or the `-A` flag) allows a remote host to use the local agent to make further SSH connections, which is useful when connecting through a bastion host. This convenience carries a risk: if the remote host is compromised while forwarding is active, it can use the forwarded agent as well.

## Common Commands

```bash
# Basic connection
ssh user@host
ssh -p 2222 user@host              # custom port

# Run a command without opening a shell
ssh user@host "df -h"

# Copy files
scp file.txt user@host:~/          # local to remote
scp user@host:~/file.txt .         # remote to local
scp -r dir/ user@host:~/           # recursive

# rsync (better for large/incremental transfers)
rsync -avz dir/ user@host:~/dir/
```

## Port Forwarding

SSH can carry arbitrary TCP traffic through its encrypted tunnel.

**Local forwarding** makes a remote service accessible as though it were running locally:

```bash
ssh -L 8080:localhost:3000 user@host
# http://localhost:8080 now hits the remote's port 3000
```

**Remote forwarding** does the reverse, exposing a local service on the remote server:

```bash
ssh -R 9090:localhost:3000 user@host
# remote's port 9090 now hits your local port 3000
```

**Dynamic forwarding** turns the connection into a SOCKS5 proxy:

```bash
ssh -D 1080 user@host
# route traffic through the proxy at localhost:1080
```

| Flag              | Type    | Direction                |
| ----------------- | ------- | ------------------------ |
| `-L local:remote` | Local   | Local machine to remote  |
| `-R remote:local` | Remote  | Remote machine to local  |
| `-D port`         | Dynamic | SOCKS5 proxy             |
| `-N`              | None    | No command, just forward |
| `-f`              | None    | Background the process   |

## Hardening the Server

The default `sshd` configuration is adequate for initial setup but should not be left in place on a production system. Relevant settings live in `/etc/ssh/sshd_config`:

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
AllowUsers deploy ubuntu
Port 2222
MaxAuthTries 3
```

Restart the service after making changes: `sudo systemctl restart sshd`

**fail2ban** is worth running on any server exposed to the internet. It bans an IP address after a set number of failed login attempts, reducing the impact of automated scanning against port 22.

## Checking and Trusting Hosts

The first connection to a new host prompts for confirmation of its fingerprint:

```
The authenticity of host '203.0.113.42' can't be established.
ED25519 key fingerprint is SHA256:abc123...
Are you sure you want to continue connecting?
```

Confirming adds the fingerprint to `~/.ssh/known_hosts`. If that fingerprint changes on a later connection, SSH refuses the connection with a prominent warning, since this typically indicates either a reinstalled server or an interception attempt. A fingerprint can be checked or cleared directly:

```bash
ssh-keyscan host 2>/dev/null | ssh-keygen -lf -   # get host fingerprint
ssh-keygen -R host                                 # remove old entry from known_hosts
```
