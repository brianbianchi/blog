# Password Attacks

Passwords are still the primary authentication mechanism for most systems, which means attacking them is still one of the most reliable paths into an environment. The techniques have evolved considerably, but the fundamentals haven't changed much: you're either guessing credentials against a live service, or you've obtained hashed credentials and you're recovering the plaintext offline.

That distinction matters a lot, because the two categories have completely different constraints and tools.

---

## Online vs Offline Attacks

**Online attacks** go directly against a live service: SSH, RDP, a login form, a VPN portal. You're rate-limited by network latency, server processing time, and potentially account lockout policies. You might get 10-50 attempts per second at best, and a single wrong guess is logged on the target. This is noisy and slow.

**Offline attacks** happen after you've obtained a hash database: the Windows SAM file, NTDS.dit from a domain controller, a dumped /etc/shadow, a breached database. You're working locally against your own hardware. A modern GPU can test billions of hashes per second. No lockout, no logging, no network dependency. This is where the real cracking happens.

Most serious engagements involve both: spray or phish your way in online, escalate privileges, dump hashes, then crack offline.

---

## Brute Force

Brute force means trying every possible combination of characters up to a given length. It's guaranteed to succeed eventually, which is cold comfort when "eventually" means centuries for anything beyond 8 characters.

Where brute force is practical:
- Short PINs (4-6 digits): trivial
- Short passwords (1-6 characters): feasible offline with GPU acceleration
- Specific character sets: if you know the password is all lowercase letters, the search space collapses

The math is straightforward. A 4-digit PIN is 10^4 = 10,000 combinations. An 8-character lowercase password is 26^8 = about 200 billion. An 8-character mixed-case alphanumeric is 62^8 = about 218 trillion. With a GPU doing 10 billion hashes per second on MD5, that's still only about 6 hours. Add special characters and length, and brute force stops being viable.

GPU acceleration is why offline cracking is so powerful. A single RTX 4090 can do roughly 164 billion MD5 hashes per second, or around 37 billion NTLMs per second. bcrypt at cost factor 10, on the other hand, drops to around 184,000 per second. That's intentional.

---

## Dictionary Attacks

Most people don't pick random passwords. They pick words, names, places, things they care about. Dictionary attacks exploit this by testing a wordlist of known and likely passwords rather than every possible combination.

The canonical wordlist is `rockyou.txt`, which comes from a 2009 breach of the RockYou social gaming site that exposed 32 million plaintext passwords. It's included in Kali at `/usr/share/wordlists/rockyou.txt`. Despite being 15 years old, it remains devastatingly effective because password habits haven't changed nearly as much as they should have.

Other useful wordlists:
- **SecLists** (Daniel Miessler's collection): covers passwords, usernames, common web paths, and much more
- **CeWL**: a tool that spiders a target website and generates a custom wordlist from the words it finds (useful for spear-targeting)
- **Company-specific wordlists**: variations of the company name, products, locations, founding year

---

## Rule-Based Attacks

This is where password cracking gets genuinely clever. A rule-based attack takes a wordlist and applies transformation rules to each word, generating variations. Hashcat and John the Ripper both have extensive rule syntaxes.

Common transformations:
- Capitalize the first letter: `password` -> `Password`
- Append numbers: `password` -> `password1`, `password123`
- Leet substitutions: `password` -> `p@ssw0rd`
- Append a symbol: `password` -> `password!`
- Combinations: `Password1!`

The reason this is so effective is that these are exactly the patterns that password complexity requirements push people toward. Tell someone their password needs a capital letter, a number, and a special character, and they'll give you `Password1!` or `Winter2024!`. These passwords satisfy the policy and fall in minutes to a decent ruleset.

Hashcat ships with several built-in rule files. The `best64.rules` file is a good starting point. `OneRuleToRuleThemAll` is a community-curated mega-ruleset that's overkill for most tasks but thorough.

```bash
# Dictionary attack with rules
hashcat -m 1000 -a 0 hashes.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

---

## Credential Stuffing

Credential stuffing is less about cracking and more about reuse. The premise: people use the same password across multiple services. Given the scale of data breaches over the past decade, there are billions of plaintext username/password pairs in circulation. Tools like `Snipr`, `SentryMBA`, or simple Python scripts test these pairs against other services automatically.

The attack is ruthlessly efficient because it requires no cracking at all. If someone used `hunter2` on LinkedIn in 2012 and LinkedIn got breached, you can try that exact credential against their corporate VPN, their email, their bank. Success rates on credential stuffing campaigns against major services are typically 0.5-2%, which sounds small until you're running millions of credentials.

The defense is straightforward and frustratingly underdeployed: don't reuse passwords, use MFA everywhere that supports it. A leaked password is meaningless if you also need the TOTP code.

---

## Password Spraying

Password spraying flips the traditional approach. Instead of trying many passwords against one account, you try one password against many accounts. This avoids triggering account lockout policies, which typically trigger after 3-5 failed attempts on a single account.

The classic targets are seasonal passwords that meet corporate complexity requirements: `Winter2024!`, `Spring2024!`, `Company2024!`, `Welcome1`. Organizations with 10,000 employees will statistically have dozens of people using these.

Spraying is particularly effective against:
- Active Directory environments where the lockout threshold is known (or default)
- O365/Azure AD portals
- VPN concentrators
- Citrix and other remote access portals

```bash
# Spraying with CrackMapExec against SMB
crackmapexec smb 10.10.10.0/24 -u users.txt -p 'Winter2024!' --continue-on-success

# Spraying with Kerbrute against Kerberos (no lockout risk with valid usernames)
kerbrute passwordspray -d domain.local users.txt 'Winter2024!'
```

One important note: Kerbrute's spray against Kerberos pre-auth doesn't trigger the same lockout counters as NTLM in many configurations, which makes it a stealthier option for spraying.

---

## Rainbow Tables

A rainbow table is a precomputed lookup table that maps hashes back to plaintexts. The idea: hash every possible password once, store the hash-to-plaintext mapping, then reverse a hash instantly with a lookup instead of computing it at query time. Elegantly lazy.

They were a real threat against unsalted hashes, and there are rainbow tables for MD5 and NTLM that cover most common passwords.

Salting completely defeats them. A salt is a random value that's unique per user and prepended (or appended) to the password before hashing. So instead of `MD5("password")`, you store `MD5("xK7q" + "password")`. Now a rainbow table would need to be precomputed for every possible salt, which is computationally infeasible. Every modern password storage system uses salts. If you encounter unsalted hashes in the wild, that's a significant red flag about the age or quality of the system.

---

## Tools

### Hashcat

Hashcat is GPU-accelerated and the fastest cracking tool available. It supports a huge range of hash types and attack modes.

```bash
# Basic syntax
hashcat -m <hash_type> -a <attack_mode> <hashfile> [wordlist/mask]

# Common hash types (-m flag)
# 0     = MD5
# 100   = SHA-1
# 1000  = NTLM
# 1800  = sha512crypt (Linux /etc/shadow)
# 3200  = bcrypt
# 5600  = NetNTLMv2
# 13100 = Kerberos 5 TGS (for Kerberoasting)

# Attack modes (-a flag)
# 0 = wordlist (dictionary)
# 1 = combination (combine two wordlists)
# 3 = brute force (mask attack)
# 6 = hybrid (wordlist + mask)
# 7 = hybrid (mask + wordlist)
```

**Mask syntax** for brute force mode uses placeholders:

| Placeholder | Character set |
|-------------|---------------|
| `?l` | lowercase letters (a-z) |
| `?u` | uppercase letters (A-Z) |
| `?d` | digits (0-9) |
| `?s` | special characters |
| `?a` | all of the above |

```bash
# Brute force: 8 chars, uppercase first, then lowercase, then 2 digits
hashcat -m 1000 -a 3 hashes.txt ?u?l?l?l?l?l?d?d

# Hybrid: rockyou words + 2-digit suffix
hashcat -m 1000 -a 6 hashes.txt rockyou.txt ?d?d

# NTLM hashes with rules
hashcat -m 1000 -a 0 hashes.txt rockyou.txt -r rules/best64.rule

# Show cracked results
hashcat -m 1000 hashes.txt --show
```

### John the Ripper

John is CPU-focused and more flexible in some ways. It has a built-in hash type auto-detection that's genuinely useful, and its incremental mode (smart brute force based on character frequency) is quite effective.

```bash
# Auto-detect hash type and crack
john hashes.txt

# With a wordlist
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

# With rules
john --wordlist=rockyou.txt --rules=best64 hashes.txt

# Show cracked passwords
john --show hashes.txt

# For specific formats
john --format=NT hashes.txt        # NTLM
john --format=sha512crypt hashes.txt
```

### Hydra and Medusa (Online Attacks)

For online attacks against live services:

```bash
# Hydra against SSH
hydra -l admin -P rockyou.txt ssh://10.10.10.5

# Hydra against a web login form
hydra -l admin -P rockyou.txt 10.10.10.5 http-post-form "/login:username=^USER^&password=^PASS^:Invalid credentials"

# Medusa against RDP
medusa -h 10.10.10.5 -u administrator -P rockyou.txt -M rdp
```

Be careful with online attacks. Account lockout is a real concern, and the noise is significant. Always scope your attack rate and lockout thresholds before running these on an engagement.

---

## Hash Identification

Recognizing a hash type by sight is a useful skill.

| Hash | Length | Looks like |
|------|--------|-----------|
| MD5 | 32 hex chars | `5f4dcc3b5aa765d61d8327deb882cf99` |
| SHA-1 | 40 hex chars | `5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8` |
| SHA-256 | 64 hex chars | `5e884898da28047151d0e56f8dc...` |
| NTLM | 32 hex chars (same length as MD5) | `8846f7eaee8fb117ad06bdd830b7586c` |
| bcrypt | starts with `$2a$`, `$2b$`, `$2y$` | `$2a$12$...` (60 chars total) |
| sha512crypt | starts with `$6$` | `$6$salt$...` (long) |
| NetNTLMv2 | structured format with `::` separators | `user::domain:challenge:hash:blob` |

NTLM and MD5 are the same length, which trips people up. Context matters: if you pulled it from a Windows SAM database, it's NTLM. If it came from a web application database, it might be MD5 (or MD5 with various wrappings). `hashid` and `hash-identifier` are command-line tools that will make educated guesses based on format.

---

## Defenses

For stored passwords, the answer is bcrypt or Argon2. Both are intentionally slow, configurable, and widely supported. SHA-256 and SHA-512 are fast hashing algorithms that are fine for file integrity but inappropriate for passwords. MD5 is simply not acceptable in 2024.

For user-facing authentication:
- **Passphrases beat complexity rules.** `correct-horse-battery-staple` is far stronger and far more memorable than `P@ssw0rd1!`. Length beats complexity every time.
- **MFA is the single most effective control** against credential attacks. Even if the password is compromised, TOTP or hardware keys stop most attackers cold.
- **Account lockout** limits online brute force. Configure it, but be aware of the denial-of-service risk.
- **Password managers** solve the reuse problem. Credential stuffing becomes useless when every site has a unique random password.
- **HIBP integration:** Services like Have I Been Pwned have an API that lets you check whether a password appears in known breach databases at enrollment time. Block those passwords.
