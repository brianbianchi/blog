# Passwords and How They're Stored

Every application that has user accounts needs to answer the same question: how do we store passwords? It sounds mundane. The answer has practical consequences for millions of people, and the history of getting it wrong reads like a catalog of preventable disasters.

## Plaintext Storage

The worst approach is storing passwords exactly as users type them. If an attacker reads your database, they have everyone's password immediately, with no additional work required. No cracking, no guessing. They can log in as any user, and because a large fraction of people reuse passwords, they can likely log in to those users' accounts on other services too.

This still happens. In 2019, Facebook acknowledged storing hundreds of millions of Instagram and Facebook passwords in plaintext in internal logs. Facebook employees could read them. That's not a breach in the traditional sense, but it's deeply wrong.

Plaintext storage is never acceptable.

## Encryption vs Hashing

A common next step is to encrypt passwords before storing them. This is better than plaintext, but it's still the wrong tool. Encryption is **reversible**: if you have the key, you can decrypt the password. That means if an attacker gets both the database and the key (which are often on the same server), they have everyone's plaintext passwords again. It also means your server can see passwords, which you don't want.

Hashing is the right direction. A cryptographic hash function takes input of any length and produces a fixed-length output (a digest). It's a one-way operation: you can compute the hash of a password, but you cannot reverse a hash to recover the password. When a user creates an account, you store the hash. When they log in, you hash the password they provide and compare it to the stored hash.

The server never needs to store, transmit, or see the actual password after the initial hashing step.

## Why MD5 and SHA-1 Are Not Enough

The obvious implementation: hash every password with SHA-256 and store the result. This is better than plaintext, but it breaks down in two ways.

**Rainbow tables.** A rainbow table is a precomputed lookup table mapping hashes back to their original inputs. Because SHA-256 is deterministic, `SHA-256("password123")` is always the same value. An attacker who has the database just looks up each hash in a precomputed table. If the password is in the table, the lookup takes milliseconds. Databases of precomputed hashes for common passwords and character combinations cover enormous swaths of what real users actually choose.

**Identical passwords produce identical hashes.** If five users all choose "Summer2023!", they all have the same stored hash. An attacker who cracks one has cracked all five simultaneously. They can also trivially see which users share passwords.

Both of these problems are solved with salting.

## Salting

A **salt** is a random value generated uniquely for each user and stored alongside their password hash. Before hashing, the salt is concatenated with the password:

```
hash = SHA-256(salt + password)
```

The salt is stored in plaintext next to the hash. This doesn't need to be secret to be effective.

Because every user has a unique random salt, identical passwords produce different hashes. Rainbow tables are rendered useless because they were built without the salt. An attacker who wants to crack passwords now has to attack each hash individually, computing hashes specifically for each user's unique salt. That's far more work.

Salts should be generated using a cryptographically secure random number generator and should be long enough (at least 16 bytes) to ensure uniqueness in practice. Using a sequential user ID as a salt, or using the username, misses the point.

## The Speed Problem

Salted SHA-256 hashes are a real improvement. But there's another issue: SHA-256 is fast. Very fast. On a modern GPU, you can compute billions of SHA-256 hashes per second. That's great for integrity checking files, and it's terrible for password storage.

An attacker with a GPU can still brute-force salted SHA-256 hashes by simply trying billions of password candidates per second. A GPU cluster running password cracking software like Hashcat can run through every combination of characters up to 8 characters long, plus every word in a dictionary with common substitutions and suffixes, in a matter of hours.

The speed of a hash function is a liability when it's being used to protect passwords. What you want is a hash function that is intentionally slow, so that checking one password candidate takes a meaningful amount of time.

## Purpose-Built Password Hashing

Several algorithms were designed specifically for this purpose. They share a key idea: tunable cost. You can set parameters that control how much CPU, time, or memory is required to compute one hash. As hardware gets faster, you turn the cost parameter up.

**bcrypt** was designed in 1999 and is still widely used. It has a work factor (commonly called the cost parameter), specified as a power of 2. At cost 12, computing one hash takes on the order of 100ms to 300ms on modern hardware. That's fine for a legitimate login. It's catastrophic for an attacker trying to brute-force millions of candidates per second. bcrypt internally salts automatically, so you don't manage the salt separately. The output is a single string containing the algorithm identifier, cost factor, salt, and hash.

```
$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXIG.Yt7.0te
```

**scrypt** adds a memory-hardness dimension. It requires not just CPU time but also a significant amount of RAM to compute. This is important because custom hardware (ASICs) can be built to do SHA-256 or even bcrypt very efficiently. Memory-hard algorithms are harder to accelerate with custom hardware because memory bandwidth is a physical constraint.

**Argon2** won the Password Hashing Competition in 2015 and is currently the recommended choice for new systems. It has three variants: Argon2d (maximizes resistance to GPU cracking), Argon2i (resistant to side-channel attacks), and **Argon2id** (hybrid, and the one most commonly recommended). Argon2id lets you tune memory usage, iterations, and parallelism independently. It's supported in most modern languages and frameworks.

A reasonable starting point for Argon2id parameters (per OWASP's guidelines):
- Memory: 19 MiB (19456 KiB)
- Iterations: 2
- Parallelism: 1

These should be revisited periodically as hardware improves.

## Pepper

In addition to a per-user salt, some systems add a **pepper**: a secret value stored on the application server (not in the database) and mixed into the hash computation. The idea is that even if an attacker exfiltrates the entire database, they still can't crack any hashes without the pepper, because they're missing a required ingredient that isn't stored anywhere in the database.

A simple way to use a pepper is to compute an HMAC over the hash using the pepper as the key, or to prepend/append it before the password hashing step. The details matter: the pepper should be generated securely, stored separately from the database (e.g., in environment variables or a secrets manager), and rotated if compromised.

Pepper is defense in depth. It makes an attacker's job harder even after a database breach, and it costs almost nothing to implement.

## Real-World Breaches Worth Knowing

**RockYou (2009).** RockYou was a social game company. They stored 32 million user passwords in plaintext. An SQL injection attack exfiltrated the entire database. The leaked dataset became the basis for `rockyou.txt`, a wordlist that ships with Kali Linux and is used in password cracking to this day. The passwords in it are real passwords that real people chose.

**LinkedIn (2012).** LinkedIn stored passwords as unsalted SHA-1 hashes. In 2012, 6.5 million hashes were posted publicly, and crackers quickly recovered the majority. The full breach turned out to be 117 million accounts and wasn't confirmed until 2016. Unsalted SHA-1 with no cost factor: a GPU can compute billions of those per second.

**Adobe (2013).** Adobe stored passwords using 3DES encryption, not hashing, and used the same key for all users. Because encryption is symmetric, identical passwords produced identical ciphertext. Attackers could look at the frequency of ciphertext values to identify common passwords, use known passwords to recover encryption keys, and then decrypt the rest. Around 150 million accounts were affected.

Each of these breaches had a different failure mode, but they all stem from the same root cause: treating password storage as a solved problem when it hadn't been thought through carefully.

## What Good Looks Like Today

Use **Argon2id** with parameters tuned to take roughly 100ms to 300ms on your hardware. Let the library manage salt generation automatically. Store the output of the hash function, which includes the salt and parameters as part of its format. Use a pepper if you want defense in depth and are willing to manage the operational complexity.

Don't use MD5, SHA-1, or SHA-256 directly for password hashing. Don't implement your own salting scheme on top of a fast hash. Don't encrypt passwords and call it secure.

If you're using a web framework, it almost certainly has a built-in password hashing abstraction. Use it. The abstraction exists so you don't have to make these decisions from scratch.

When hardware gets faster, you increase the work factor and re-hash passwords at next login. This is standard practice and well-supported by the algorithms designed for this purpose. Security here isn't a one-time decision; it's a parameter you revisit.
