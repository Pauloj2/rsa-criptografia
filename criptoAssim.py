"""
RSA Cryptography - Implementação Manual Completa
Sem uso de bibliotecas de criptografia prontas
"""

import random
import math


# ─────────────────────────────────────────────
# 1. ARITMÉTICA MODULAR E PRIMALIDADE
# ─────────────────────────────────────────────

def is_prime_miller_rabin(n: int, k: int = 20) -> bool:
    """
    Teste de primalidade de Miller-Rabin (probabilístico).
    Retorna True se n é (provavelmente) primo.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Escreve n-1 como 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Testemunhas
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = mod_pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(r - 1):
            x = mod_pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def mod_pow(base: int, exp: int, mod: int) -> int:
    """
    Exponenciação modular rápida: base^exp mod mod
    Algoritmo: Square-and-Multiply
    Complexidade: O(log exp)
    """
    result = 1
    base %= mod
    while exp > 0:
        if exp % 2 == 1:          # bit menos significativo = 1
            result = (result * base) % mod
        exp >>= 1                  # desloca bits à direita (divide por 2)
        base = (base * base) % mod
    return result


def gcd(a: int, b: int) -> int:
    """Máximo Divisor Comum - Algoritmo de Euclides."""
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int):
    """
    Algoritmo de Euclides Estendido.
    Retorna (g, x, y) tal que: a*x + b*y = g = gcd(a, b)
    """
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y


def mod_inverse(a: int, m: int) -> int:
    """
    Inverso multiplicativo modular de a em Z_m.
    Encontra x tal que: a * x ≡ 1 (mod m)
    Usa o Algoritmo de Euclides Estendido.
    Lança ValueError se o inverso não existe.
    """
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"Inverso modular não existe: gcd({a}, {m}) = {g} ≠ 1")
    return x % m


# ─────────────────────────────────────────────
# 2. GERAÇÃO DE NÚMEROS PRIMOS GRANDES
# ─────────────────────────────────────────────

def generate_prime(bits: int) -> int:
    """
    Gera um número primo aleatório com exatamente `bits` bits.
    Estratégia:
      1. Gera número aleatório ímpar no intervalo correto.
      2. Aplica Miller-Rabin até encontrar um primo.
    """
    while True:
        # Garante que o número tem exatamente `bits` bits
        n = random.getrandbits(bits)
        # Força o bit mais significativo (tamanho correto)
        n |= (1 << (bits - 1))
        # Força ímpar (números pares > 2 não são primos)
        n |= 1

        if is_prime_miller_rabin(n):
            return n


# ─────────────────────────────────────────────
# 3. GERAÇÃO DO PAR DE CHAVES RSA
# ─────────────────────────────────────────────

def generate_keys(bits: int = 512):
    """
    Gera par de chaves RSA.

    Processo:
      1. Escolhe dois primos grandes p e q  (bits/2 cada)
      2. Calcula n = p * q  (módulo RSA)
      3. Calcula φ(n) = (p-1)(q-1)  (Totiente de Euler)
      4. Escolhe e tal que: 1 < e < φ(n)  e  gcd(e, φ(n)) = 1
      5. Calcula d = e^(-1) mod φ(n)  (via Euclides Estendido)

    Retorna:
      public_key  = (e, n)
      private_key = (d, n)
    """
    half = bits // 2

    print(f"  Gerando primo p ({half} bits)...", end=" ", flush=True)
    p = generate_prime(half)
    print("✓")

    print(f"  Gerando primo q ({half} bits)...", end=" ", flush=True)
    q = generate_prime(half)
    # Garante p ≠ q
    while q == p:
        q = generate_prime(half)
    print("✓")

    n = p * q
    phi_n = (p - 1) * (q - 1)

    # e padrão: 65537 = 2^16 + 1  (primo de Fermat, eficiente e seguro)
    e = 65537
    if gcd(e, phi_n) != 1:
        # Fallback: busca outro e
        e = 3
        while gcd(e, phi_n) != 1:
            e += 2

    print("  Calculando expoente de decifragem d...", end=" ", flush=True)
    d = mod_inverse(e, phi_n)
    print("✓")

    return (e, n), (d, n), p, q, phi_n


# ─────────────────────────────────────────────
# 4. CIFRAGEM E DECIFRAGEM
# ─────────────────────────────────────────────

def text_to_int(text: str) -> int:
    """Converte string UTF-8 → inteiro (big-endian)."""
    return int.from_bytes(text.encode("utf-8"), byteorder="big")


def int_to_text(n: int) -> str:
    """Converte inteiro → string UTF-8."""
    length = (n.bit_length() + 7) // 8
    return n.to_bytes(length, byteorder="big").decode("utf-8")


def encrypt(message: str, public_key: tuple) -> list[int]:
    """
    Cifra uma mensagem usando a chave pública (e, n).

    Divide a mensagem em blocos menores que n para garantir
    que m < n (requisito da aritmética modular RSA).

    C = M^e mod n
    """
    e, n = public_key
    # Tamanho máximo do bloco em bytes (deixa 1 byte de margem)
    block_size = (n.bit_length() // 8) - 1

    encoded = message.encode("utf-8")
    ciphertext = []

    for i in range(0, len(encoded), block_size):
        block = encoded[i:i + block_size]
        m = int.from_bytes(block, byteorder="big")
        c = mod_pow(m, e, n)
        ciphertext.append(c)

    return ciphertext


def decrypt(ciphertext: list[int], private_key: tuple) -> str:
    """
    Decifra uma lista de blocos usando a chave privada (d, n).

    M = C^d mod n
    """
    d, n = private_key
    block_size = (n.bit_length() // 8) - 1

    plaintext_bytes = b""

    for c in ciphertext:
        m = mod_pow(c, d, n)
        # Reconstrói bytes do bloco
        block_bytes = m.to_bytes(block_size, byteorder="big").lstrip(b"\x00")
        plaintext_bytes += block_bytes

    return plaintext_bytes.decode("utf-8")


# ─────────────────────────────────────────────
# 5. INTERFACE DE LINHA DE COMANDO
# ─────────────────────────────────────────────

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          RSA — Rivest-Shamir-Adleman Cipher                  ║
║          Implementação Manual  |  Python (sem libs crypto)   ║
╚══════════════════════════════════════════════════════════════╝
""")


def print_key_info(pub, priv, p, q, phi_n):
    e, n = pub
    d, _ = priv
    print("\n━━━━━━━━━━━━━━━━━━━━━━ CHAVES GERADAS ━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  p (primo)  = {p}")
    print(f"  q (primo)  = {q}")
    print(f"  n = p×q    = {n}")
    print(f"  φ(n)       = {phi_n}")
    print(f"\n  🔑 Chave Pública  (e, n):")
    print(f"     e = {e}")
    print(f"     n = {n}")
    print(f"\n  🔐 Chave Privada  (d, n):")
    print(f"     d = {d}")
    print(f"     n = {n}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def demo_mode():
    """Executa demonstração completa automaticamente."""
    print_banner()
    print("[ MODO DEMONSTRAÇÃO ]\n")

    # Gerar chaves
    print("▶ Gerando par de chaves RSA (512 bits)...")
    pub, priv, p, q, phi_n = generate_keys(bits=512)
    print_key_info(pub, priv, p, q, phi_n)

    # Cifrar
    message = "RSA funciona! Segurança assimétrica com aritmética modular."
    print(f"\n▶ Mensagem original:\n   \"{message}\"")

    print("\n▶ Cifrando com chave pública...")
    cipher = encrypt(message, pub)
    print(f"   Blocos cifrados ({len(cipher)} bloco(s)):")
    for i, c in enumerate(cipher):
        print(f"   [{i}] {c}")

    # Decifrar
    print("\n▶ Decifrando com chave privada...")
    recovered = decrypt(cipher, priv)
    print(f"   Mensagem recuperada:\n   \"{recovered}\"")

    # Verificação
    print("\n▶ Verificação:")
    ok = message == recovered
    print(f"   Mensagem original == Mensagem decifrada? {'✅ SIM' if ok else '❌ NÃO'}")

    # Teste adicional
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("▶ Teste com emojis e caracteres UTF-8:")
    msg2 = "Olá, mundo! 🌍 Criptografia é incrível! 🔐"
    print(f"   Original: \"{msg2}\"")
    c2 = encrypt(msg2, pub)
    r2 = decrypt(c2, priv)
    print(f"   Decifrado: \"{r2}\"")
    print(f"   Correto? {'✅ SIM' if msg2 == r2 else '❌ NÃO'}")


def interactive_mode():
    """Modo interativo com menu."""
    print_banner()

    pub = priv = None

    while True:
        print("\n┌─────────────────────────────────┐")
        print("│  MENU RSA                       │")
        print("│  1. Gerar par de chaves         │")
        print("│  2. Cifrar mensagem             │")
        print("│  3. Decifrar mensagem           │")
        print("│  4. Demonstração completa       │")
        print("│  5. Sair                        │")
        print("└─────────────────────────────────┘")
        op = input("  Opção: ").strip()

        if op == "1":
            bits_str = input("  Bits (recomendado 512 ou 1024) [512]: ").strip()
            bits = int(bits_str) if bits_str.isdigit() else 512
            print(f"\n  Gerando chaves RSA de {bits} bits...")
            pub, priv, p, q, phi_n = generate_keys(bits)
            print_key_info(pub, priv, p, q, phi_n)

        elif op == "2":
            if not pub:
                print("  ⚠ Gere as chaves primeiro (opção 1).")
                continue
            msg = input("  Mensagem a cifrar: ")
            cipher = encrypt(msg, pub)
            print(f"\n  Texto cifrado ({len(cipher)} bloco(s)):")
            for i, c in enumerate(cipher):
                print(f"  [{i}] {c}")

        elif op == "3":
            if not priv:
                print("  ⚠ Gere as chaves primeiro (opção 1).")
                continue
            raw = input("  Cole os blocos cifrados separados por vírgula:\n  > ")
            try:
                cipher = [int(x.strip()) for x in raw.split(",")]
                result = decrypt(cipher, priv)
                print(f"\n  Mensagem decifrada: \"{result}\"")
            except Exception as ex:
                print(f"  ❌ Erro ao decifrar: {ex}")

        elif op == "4":
            demo_mode()

        elif op == "5":
            print("\n  Até logo! 🔐\n")
            break

        else:
            print("  Opção inválida.")


# ─────────────────────────────────────────────
# PONTO DE ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        interactive_mode()