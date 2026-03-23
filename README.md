# 🔐 RSA Cryptography — Manual Implementation in Python

Complete implementation of the **RSA (Rivest-Shamir-Adleman)** algorithm built from scratch in pure Python, without any external cryptography libraries. The project covers everything from large prime number generation to UTF-8 message encryption and decryption.

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Mathematical Foundations](#mathematical-foundations)
- [Code Structure](#code-structure)
- [How to Use](#how-to-use)
- [Sample Output](#sample-output)
- [Limitations and Security](#limitations-and-security)
- [Requirements](#requirements)

---

## About the Project

RSA is one of the most widely used asymmetric encryption algorithms in the world. It works with a **key pair**:

- **Public key** `(e, n)` — used to **encrypt** the message. Can be shared freely.
- **Private key** `(d, n)` — used to **decrypt** the message. Must be kept secret.

The security of RSA relies on the computational difficulty of **factoring very large integers** — a problem for which no efficient solution is known on classical computers.

---

<img width="1159" height="891" alt="image" src="https://github.com/user-attachments/assets/ea3ecca2-dab6-46ea-b223-5aa9295056dc" />


## Mathematical Foundations

### 1. Key Generation

The key generation process follows these steps:

| Step | Operation | Description |
|------|-----------|-------------|
| 1 | Choose `p` and `q` | Two large, distinct prime numbers |
| 2 | Compute `n = p × q` | RSA modulus (public component) |
| 3 | Compute `φ(n) = (p-1)(q-1)` | Euler's Totient Function |
| 4 | Choose `e` | Integer such that `1 < e < φ(n)` and `gcd(e, φ(n)) = 1` |
| 5 | Compute `d = e⁻¹ mod φ(n)` | Decryption exponent (via Extended Euclidean Algorithm) |

The value `e = 65537` (Fermat prime, `2¹⁶ + 1`) is used by default — a widely adopted choice in practice for being both efficient and secure.

### 2. Encryption

```
C = M^e mod n
```

The message `M` (represented as an integer) is raised to the public exponent `e` modulo `n`, producing the ciphertext `C`.

### 3. Decryption

```
M = C^d mod n
```

The ciphertext `C` is raised to the private exponent `d` modulo `n`, recovering the original message `M`.

### 4. Why Does It Work?

By **Euler's Theorem**, we have:

```
M^(φ(n)) ≡ 1 (mod n),  for gcd(M, n) = 1
```

Since `d` is the modular inverse of `e` modulo `φ(n)`, we have `e × d ≡ 1 (mod φ(n))`, and therefore:

```
C^d = (M^e)^d = M^(e×d) ≡ M (mod n)
```

---

## Code Structure

```
criptoAssim.py
├── 1. Modular Arithmetic and Primality
│   ├── is_prime_miller_rabin()   — Miller-Rabin primality test (probabilistic)
│   ├── mod_pow()                 — Fast modular exponentiation (Square-and-Multiply)
│   ├── gcd()                     — Greatest Common Divisor (Euclidean Algorithm)
│   ├── extended_gcd()            — Extended Euclidean: returns g, x, y such that ax + by = g
│   └── mod_inverse()             — Modular multiplicative inverse
│
├── 2. Large Prime Generation
│   └── generate_prime()          — Generates a random N-bit prime
│
├── 3. Key Pair Generation
│   └── generate_keys()           — Returns (public_key, private_key, p, q, φ(n))
│
├── 4. Encryption and Decryption
│   ├── text_to_int() / int_to_text()  — Conversion between UTF-8 text and integer
│   ├── encrypt()                       — Encrypts message in blocks: C = M^e mod n
│   └── decrypt()                       — Decrypts blocks: M = C^d mod n
│
└── 5. Interface
    ├── demo_mode()               — Full automatic demonstration
    └── interactive_mode()        — Interactive menu (encrypt, decrypt, generate keys)
```

### Implemented Algorithms

**Miller-Rabin** — Probabilistic primality test with `k = 20` rounds. The probability of a composite number passing the test is at most `4⁻²⁰ ≈ 10⁻¹²`.

**Square-and-Multiply** — Modular exponentiation in `O(log exp)` operations, essential for making `M^e mod n` feasible with exponents and moduli of hundreds of bits.

**Extended Euclidean Algorithm** — Computes the modular inverse of `e` in `φ(n)`, obtaining the decryption exponent `d`.

**Message blocks** — The message is split into blocks of `(bits_n / 8) - 1` bytes to ensure each block `M < n`, a mandatory requirement of RSA arithmetic.

---

## How to Use

### Requirements

- Python 3.10 or higher (no external dependencies)

### Demo Mode

Automatically runs key generation, encryption, and decryption:

```bash
python criptoAssim.py --demo
```

### Interactive Mode

Opens a menu with options for key generation, encryption, and manual decryption:

```bash
python criptoAssim.py
```

#### Menu options:

```
1. Generate key pair      — choose the key size in bits (512, 1024...)
2. Encrypt message        — uses the generated public key
3. Decrypt message        — uses the generated private key
4. Full demonstration     — runs the complete flow automatically
5. Exit
```

---

## Sample Output

```
▶ Generating RSA key pair (512 bits)...
  Generating prime p (256 bits)... ✓
  Generating prime q (256 bits)... ✓
  Computing decryption exponent d... ✓

━━━━━━━━━━━━━━━━ GENERATED KEYS ━━━━━━━━━━━━━━━━
  🔑 Public Key  (e, n):
     e = 65537
     n = 9823...4471   (512-bit number)

  🔐 Private Key  (d, n):
     d = 7214...3309
     n = 9823...4471
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶ Original message:
   "RSA works! Asymmetric security with modular arithmetic."

▶ Encrypting with public key...
   Encrypted blocks (2 block(s)):
   [0] 38271...9042
   [1] 71049...2218

▶ Decrypting with private key...
   Recovered message:
   "RSA works! Asymmetric security with modular arithmetic."

▶ Verification:
   Original message == Decrypted message? ✅ YES
```

---

## Limitations and Security

> ⚠️ This project is intended for **educational purposes only**. It should not be used in production systems.

- **Key size**: 512 bits is insufficient for real-world use. The current standard recommends a **minimum of 2048 bits**, with 4096 bits for high security.
- **No padding**: The implementation does not use padding schemes such as OAEP (PKCS#1 v2), making it vulnerable to chosen-ciphertext attacks.
- **Key management**: Keys are generated and displayed in memory, with no secure storage.
- **Side-channel**: There is no protection against timing attacks.

For production use, rely on audited libraries such as `cryptography` (Python) or `OpenSSL`.

---

## Requirements

| Item | Version |
|------|---------|
| Python | ≥ 3.10 |
| External libraries | None |

Only the Python standard library is used (`random`, `math`, `sys`).

---

## References

- Rivest, R. L., Shamir, A., & Adleman, L. (1978). *A method for obtaining digital signatures and public-key cryptosystems*. Communications of the ACM.
- Cormen, T. H. et al. *Introduction to Algorithms* — Chapters on number theory and cryptography.
- NIST FIPS 186-5 — Standards for cryptographic key generation.
