# 🔐 RSA Cryptography — Implementação Manual em Python

Implementação completa do algoritmo **RSA (Rivest-Shamir-Adleman)** feita do zero em Python puro, sem uso de bibliotecas de criptografia externas. O projeto cobre desde a geração de números primos grandes até a cifragem e decifragem de mensagens UTF-8.

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Fundamentos Matemáticos](#fundamentos-matemáticos)
- [Estrutura do Código](#estrutura-do-código)
- [Como Usar](#como-usar)
- [Exemplo de Saída](#exemplo-de-saída)
- [Limitações e Segurança](#limitações-e-segurança)
- [Requisitos](#requisitos)

---

## Sobre o Projeto

RSA é um dos algoritmos de criptografia assimétrica mais utilizados no mundo. Ele funciona com um **par de chaves**:

- **Chave pública** `(e, n)` — usada para **cifrar** a mensagem. Pode ser compartilhada livremente.
- **Chave privada** `(d, n)` — usada para **decifrar** a mensagem. Deve ser mantida em segredo.

A segurança do RSA baseia-se na dificuldade computacional de **fatorar números inteiros muito grandes** — um problema para o qual não se conhece solução eficiente em computadores clássicos.

---

<img width="1159" height="891" alt="image" src="https://github.com/user-attachments/assets/ea3ecca2-dab6-46ea-b223-5aa9295056dc" />


## Fundamentos Matemáticos

### 1. Geração das Chaves

O processo de geração de chaves segue os seguintes passos:

| Passo | Operação | Descrição |
|-------|----------|-----------|
| 1 | Escolher `p` e `q` | Dois números primos grandes e distintos |
| 2 | Calcular `n = p × q` | Módulo RSA (parte pública) |
| 3 | Calcular `φ(n) = (p-1)(q-1)` | Função Totiente de Euler |
| 4 | Escolher `e` | Inteiro tal que `1 < e < φ(n)` e `mdc(e, φ(n)) = 1` |
| 5 | Calcular `d = e⁻¹ mod φ(n)` | Expoente de decifragem (via Euclides Estendido) |

O valor `e = 65537` (primo de Fermat, `2¹⁶ + 1`) é usado por padrão — é uma escolha amplamente adotada na prática por ser eficiente e seguro.

### 2. Cifragem

```
C = M^e mod n
```

A mensagem `M` (representada como inteiro) é elevada ao expoente público `e` módulo `n`, produzindo o criptograma `C`.

### 3. Decifragem

```
M = C^d mod n
```

O criptograma `C` é elevado ao expoente privado `d` módulo `n`, recuperando a mensagem original `M`.

### 4. Por que funciona?

Pelo **Teorema de Euler**, temos que:

```
M^(φ(n)) ≡ 1 (mod n),  para mdc(M, n) = 1
```

Como `d` é o inverso de `e` módulo `φ(n)`, temos `e × d ≡ 1 (mod φ(n))`, e portanto:

```
C^d = (M^e)^d = M^(e×d) ≡ M (mod n)
```

---

## Estrutura do Código

```
criptoAssim.py
├── 1. Aritmética Modular e Primalidade
│   ├── is_prime_miller_rabin()   — Teste de Miller-Rabin (probabilístico)
│   ├── mod_pow()                 — Exponenciação modular rápida (Square-and-Multiply)
│   ├── gcd()                     — Máximo Divisor Comum (Algoritmo de Euclides)
│   ├── extended_gcd()            — Euclides Estendido: retorna g, x, y tal que ax + by = g
│   └── mod_inverse()             — Inverso multiplicativo modular
│
├── 2. Geração de Primos Grandes
│   └── generate_prime()          — Gera primo aleatório de N bits
│
├── 3. Geração do Par de Chaves
│   └── generate_keys()           — Retorna (chave_pública, chave_privada, p, q, φ(n))
│
├── 4. Cifragem e Decifragem
│   ├── text_to_int() / int_to_text()  — Conversão entre texto UTF-8 e inteiro
│   ├── encrypt()                       — Cifra mensagem em blocos: C = M^e mod n
│   └── decrypt()                       — Decifra blocos: M = C^d mod n
│
└── 5. Interface
    ├── demo_mode()               — Demonstração automática completa
    └── interactive_mode()        — Menu interativo (cifrar, decifrar, gerar chaves)
```

### Algoritmos Implementados

**Miller-Rabin** — Teste probabilístico de primalidade com `k = 20` rodadas. A probabilidade de um composto passar no teste é no máximo `4⁻²⁰ ≈ 10⁻¹²`.

**Square-and-Multiply** — Exponenciação modular em `O(log exp)` operações, essencial para tornar `M^e mod n` viável com expoentes e módulos de centenas de bits.

**Algoritmo de Euclides Estendido** — Calcula o inverso modular de `e` em `φ(n)`, obtendo o expoente de decifragem `d`.

**Blocos de mensagem** — A mensagem é dividida em blocos de `(bits_n / 8) - 1` bytes para garantir que cada bloco `M < n`, requisito obrigatório da aritmética RSA.

---

## Como Usar

### Requisitos

- Python 3.10 ou superior (sem dependências externas)

### Modo Demonstração

Executa automaticamente a geração de chaves, cifragem e decifragem:

```bash
python criptoAssim.py --demo
```

### Modo Interativo

Abre um menu com opções de geração de chaves, cifragem e decifragem manual:

```bash
python criptoAssim.py
```

#### Opções do menu:

```
1. Gerar par de chaves      — escolha o tamanho em bits (512, 1024...)
2. Cifrar mensagem          — usa a chave pública gerada
3. Decifrar mensagem        — usa a chave privada gerada
4. Demonstração completa    — executa o fluxo completo automaticamente
5. Sair
```

---

## Exemplo de Saída

```
▶ Gerando par de chaves RSA (512 bits)...
  Gerando primo p (256 bits)... ✓
  Gerando primo q (256 bits)... ✓
  Calculando expoente de decifragem d... ✓

━━━━━━━━━━━━━━━━ CHAVES GERADAS ━━━━━━━━━━━━━━━━
  🔑 Chave Pública  (e, n):
     e = 65537
     n = 9823...4471   (número de 512 bits)

  🔐 Chave Privada  (d, n):
     d = 7214...3309
     n = 9823...4471
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶ Mensagem original:
   "RSA funciona! Segurança assimétrica com aritmética modular."

▶ Cifrando com chave pública...
   Blocos cifrados (2 bloco(s)):
   [0] 38271...9042
   [1] 71049...2218

▶ Decifrando com chave privada...
   Mensagem recuperada:
   "RSA funciona! Segurança assimétrica com aritmética modular."

▶ Verificação:
   Mensagem original == Mensagem decifrada? ✅ SIM
```

---

## Limitações e Segurança

> ⚠️ Este projeto tem **fins educacionais**. Não deve ser usado em sistemas de produção.

- **Tamanho de chave**: 512 bits é insuficiente para uso real. O padrão atual recomenda **mínimo de 2048 bits**, com 4096 bits para alta segurança.
- **Sem padding**: A implementação não utiliza esquemas de padding como OAEP (PKCS#1 v2), tornando-a vulnerável a ataques de texto cifrado escolhido.
- **Gerenciamento de chaves**: As chaves são geradas e exibidas em memória, sem armazenamento seguro.
- **Side-channel**: Não há proteção contra ataques de temporização (*timing attacks*).

Para uso em produção, utilize bibliotecas auditadas como `cryptography` (Python) ou `OpenSSL`.

---

## Requisitos

| Item | Versão |
|------|--------|
| Python | ≥ 3.10 |
| Bibliotecas externas | Nenhuma |

Apenas a biblioteca padrão do Python é utilizada (`random`, `math`, `sys`).

---

## Referências

- Rivest, R. L., Shamir, A., & Adleman, L. (1978). *A method for obtaining digital signatures and public-key cryptosystems*. Communications of the ACM.
- Cormen, T. H. et al. *Introduction to Algorithms* — Capítulos sobre teoria dos números e criptografia.
- NIST FIPS 186-5 — Padrões para geração de chaves criptográficas.
