# Cryptography Explained Simply

Cryptography is the practice of securing communication so that only the intended parties can read it. That sounds narrow, but it extends to a lot of things you depend on every day: HTTPS, password storage, software update signing, and two-factor authentication all rely on cryptographic primitives. Understanding the basics doesn't require a math degree. It does require keeping a few distinct concepts separate.

## What Cryptography Is Actually For

Cryptography serves three core goals:

- **Confidentiality:** Only the intended recipient can read the message.
- **Integrity:** The message hasn't been altered in transit.
- **Authentication:** You can verify who sent the message (or who you're talking to).

Not every cryptographic tool addresses all three at once. Hashing gives you integrity but not confidentiality. Encryption gives you confidentiality but doesn't inherently prove who encrypted it. A digital signature gives you authentication and integrity but not confidentiality. You often need to combine primitives to get everything you want.

## Symmetric Encryption

Symmetric encryption uses a single key for both encryption and decryption. If Alice and Bob both have the same key, Alice can encrypt a message, send it, and Bob can decrypt it. Anyone without the key sees ciphertext.

The dominant symmetric algorithm today is **AES (Advanced Encryption Standard)**. It operates on fixed-size blocks of data and supports key lengths of 128, 192, or 256 bits. AES-128 is considered secure; AES-256 is what most people use when they want to be conservative or meet certain compliance requirements. Both are fast enough to encrypt gigabytes of data per second on modern hardware.

Older symmetric algorithms like **DES** (56-bit key) and **3DES** are broken or deprecated. DES can be brute-forced in a matter of hours with off-the-shelf hardware. Don't use them.

The fundamental problem with symmetric encryption is key distribution: how do Alice and Bob agree on the same key without an attacker intercepting it? If they can't meet in person, they have a problem. This is the problem asymmetric encryption was designed to solve.

## Asymmetric Encryption

Asymmetric encryption uses a key pair: a **public key** and a **private key**. They're mathematically linked, but knowing the public key doesn't let you derive the private key (at least not in any reasonable amount of time).

Here's how it solves the key distribution problem. Bob publishes his public key. Alice uses it to encrypt a message. The only key that can decrypt that message is Bob's private key, which Bob has never shared with anyone. Even Alice, after encrypting the message, can't decrypt it.

The most well-known asymmetric algorithm is **RSA**, which relies on the computational difficulty of factoring the product of two large prime numbers. RSA is secure with key sizes of 2048 bits or larger; 1024-bit RSA is considered too weak now. More modern elliptic curve algorithms (ECDH, Ed25519) achieve equivalent security with much smaller keys, which is why they've become preferred in new systems.

The downside of asymmetric encryption is that it's much slower than symmetric encryption. Encrypting large amounts of data with RSA directly is impractical. Which leads to the next concept.

## Hybrid Encryption

In practice, asymmetric encryption is used to establish a shared secret, and then symmetric encryption does the actual heavy lifting. This is called hybrid encryption, and it's how TLS works.

When you connect to an HTTPS site:

1. The server sends its public key (in its certificate).
2. Your browser and the server perform a key exchange (often using Diffie-Hellman or its elliptic curve variant, ECDH) to arrive at a shared symmetric key that neither side transmitted directly.
3. The rest of the session uses that symmetric key with AES to encrypt the actual traffic.

You get the key distribution advantage of asymmetric cryptography and the speed of symmetric encryption. This combination is everywhere.

## Hashing

A cryptographic hash function takes an input of any size and produces a fixed-length output, called a digest or hash. Three important properties:

1. **One-way:** You cannot recover the original input from the hash.
2. **Deterministic:** The same input always produces the same hash.
3. **Collision-resistant:** It should be computationally infeasible to find two different inputs that produce the same hash.

**SHA-256** produces a 256-bit digest and is currently the workhorse of hashing. **SHA-3** is the newer NIST standard, based on a completely different design, and is also secure.

**MD5** and **SHA-1** are broken. Researchers have demonstrated practical collision attacks against both, meaning you can craft two different inputs that produce the same hash. For SHA-1, Google's SHAttered attack in 2017 produced two different PDF files with identical SHA-1 hashes. Don't use either for any security purpose.

Hashing is used for:
- **Integrity verification:** A software vendor publishes a SHA-256 hash of their installer. You hash the file you downloaded and compare. If they match, nothing was tampered with.
- **Password storage:** Servers store a hash of your password, not the password itself. More on why this gets complicated below.
- **Digital signatures:** Signing the hash of a document rather than the document itself.

## MACs: Hashing with a Secret Key

A regular hash doesn't prove who created it. Anyone can compute `SHA-256("hello")`. A **Message Authentication Code (MAC)** solves this by mixing a secret key into the computation.

**HMAC (Hash-based MAC)** is the standard construction. It combines a secret key with the message before hashing in a way that prevents certain attacks. If Alice and Bob share a secret key, Alice can send a message along with its HMAC. Bob recomputes the HMAC using the shared key and the received message. If they match, the message is authentic and unaltered.

MACs give you both integrity and authentication, as long as the key stays secret. They don't give you non-repudiation, because anyone who has the key could have generated the MAC. That's where digital signatures come in.

## Digital Signatures

A digital signature uses asymmetric keys, but in reverse. Alice signs with her **private key**. Anyone with her **public key** can verify the signature.

The typical process:

1. Alice computes a hash of the document.
2. She encrypts that hash with her private key. That encrypted hash is the signature.
3. Bob decrypts the signature using Alice's public key, recovering the hash.
4. Bob independently hashes the document and compares. If they match, the document is authentic and hasn't been modified, and only Alice could have produced that signature (she's the only one with her private key).

Digital signatures are used in TLS certificates, code signing, email authentication (S/MIME), and software package verification. They provide authentication, integrity, and non-repudiation.

## Common Weaknesses

Cryptography fails in predictable ways. The algorithms themselves are rarely the problem; it's the implementation and configuration.

**Weak algorithms:** DES, MD5 for integrity purposes, RC4 (a stream cipher with serious statistical biases). These show up in legacy systems and IoT devices all the time. Their presence is a finding.

**Short key lengths:** RSA-1024 is too short. Elliptic curve keys below 224 bits are too short. Key length requirements have increased as compute has become cheaper.

**ECB mode:** AES is a block cipher that encrypts one fixed-size block at a time. If you encrypt multiple blocks independently (ECB mode), identical plaintext blocks produce identical ciphertext blocks. This leaks structural information about the plaintext. The famous illustration of this is the ECB penguin: encrypt a bitmap image of a penguin using ECB mode and the shape of the penguin is still visible in the ciphertext, because the white pixels in one block of the image produce the same ciphertext as the same white pixels in another block. CBC, CTR, and GCM modes don't have this problem.

**IV reuse:** Many cipher modes require an initialization vector (IV) to randomize encryption so that the same plaintext encrypted twice produces different ciphertext. If the IV is reused with the same key, an attacker can recover information about the plaintext. In some modes (CTR, GCM), IV reuse is catastrophic and completely breaks the encryption.

**Deprecated TLS versions:** TLS 1.0 and 1.1 support cipher suites and algorithms that are no longer considered safe. TLS 1.2 with appropriate ciphers is acceptable; TLS 1.3 is the current standard and removes most of the legacy footguns.

The practical takeaway is: don't invent your own cryptography, don't configure deprecated algorithms to keep compatibility with old clients, and don't generate static IVs. Use well-maintained libraries that make good choices by default, and stay current on what's considered safe.
