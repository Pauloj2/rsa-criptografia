"""
RSA Cryptography — Interface Gráfica (Tkinter)
Importa as funções de criptoAssim.py
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from criptoAssim import generate_keys, encrypt, decrypt

# ─────────────────────────────────────────────
# PALETA DE CORES
# ─────────────────────────────────────────────
BG        = "#1a1a2e"   # fundo principal
PANEL     = "#16213e"   # fundo dos painéis
ACCENT    = "#0f3460"   # bordas / cabeçalhos
HIGHLIGHT = "#e94560"   # botões / destaques
TEXT      = "#eaeaea"   # texto principal
SUBTEXT   = "#a0a0c0"   # texto secundário
SUCCESS   = "#4ecca3"   # verde-sucesso
WARNING   = "#f5a623"   # laranja-aviso
ENTRY_BG  = "#0d1b2a"   # fundo de campos de texto
MONO      = ("Consolas", 9)
FONT      = ("Segoe UI", 10)
FONT_B    = ("Segoe UI", 10, "bold")
FONT_H    = ("Segoe UI", 13, "bold")


class RSAApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RSA Cipher — Implementação Manual")
        self.geometry("920x680")
        self.minsize(820, 600)
        self.configure(bg=BG)
        self.resizable(True, True)

        # Estado
        self.pub_key  = None
        self.priv_key = None
        self.cipher_blocks: list[int] = []

        self._build_header()
        self._build_notebook()
        self._build_status()

    # ── Header ──────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔐  RSA — Rivest-Shamir-Adleman",
                 font=("Segoe UI", 15, "bold"), bg=ACCENT, fg=TEXT).pack()
        tk.Label(hdr, text="Implementação manual · sem bibliotecas de criptografia",
                 font=("Segoe UI", 9), bg=ACCENT, fg=SUBTEXT).pack()

    # ── Notebook (abas) ─────────────────────────────────────────────
    def _build_notebook(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",        background=BG,    borderwidth=0)
        style.configure("TNotebook.Tab",    background=ACCENT, foreground=TEXT,
                        font=FONT_B, padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", HIGHLIGHT)],
                  foreground=[("selected", "#ffffff")])
        style.configure("TFrame", background=BG)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=8)

        self.tab_keys    = ttk.Frame(nb)
        self.tab_encrypt = ttk.Frame(nb)
        self.tab_decrypt = ttk.Frame(nb)

        nb.add(self.tab_keys,    text="  🔑  Chaves  ")
        nb.add(self.tab_encrypt, text="  🔒  Cifrar  ")
        nb.add(self.tab_decrypt, text="  🔓  Decifrar  ")

        self._build_tab_keys()
        self._build_tab_encrypt()
        self._build_tab_decrypt()

    # ── Aba: Chaves ─────────────────────────────────────────────────
    def _build_tab_keys(self):
        tab = self.tab_keys
        tab.configure(style="TFrame")

        # Controles
        ctrl = tk.Frame(tab, bg=PANEL, padx=16, pady=12)
        ctrl.pack(fill="x", padx=12, pady=(12, 4))

        tk.Label(ctrl, text="Tamanho das chaves:", font=FONT_B,
                 bg=PANEL, fg=TEXT).grid(row=0, column=0, sticky="w")

        self.bits_var = tk.StringVar(value="512")
        bits_combo = ttk.Combobox(ctrl, textvariable=self.bits_var,
                                  values=["256", "512", "1024"], width=8,
                                  state="readonly", font=FONT)
        bits_combo.grid(row=0, column=1, padx=10)

        self.btn_gen = tk.Button(
            ctrl, text="Gerar Par de Chaves", font=FONT_B,
            bg=HIGHLIGHT, fg="#ffffff", activebackground="#c73652",
            relief="flat", padx=18, pady=6, cursor="hand2",
            command=self._generate_keys
        )
        self.btn_gen.grid(row=0, column=2, padx=10)

        self.key_status = tk.Label(ctrl, text="Nenhuma chave gerada.", font=FONT,
                                   bg=PANEL, fg=WARNING)
        self.key_status.grid(row=0, column=3, padx=14)

        # Indicador de progresso
        self.progress = ttk.Progressbar(tab, mode="indeterminate", length=200)

        # Área de exibição das chaves
        tk.Label(tab, text="Detalhes das Chaves", font=FONT_H,
                 bg=BG, fg=SUBTEXT).pack(anchor="w", padx=16, pady=(8, 2))

        self.keys_text = scrolledtext.ScrolledText(
            tab, wrap="word", font=MONO, bg=ENTRY_BG, fg=TEXT,
            insertbackground=TEXT, bd=0, relief="flat",
            highlightthickness=1, highlightbackground=ACCENT
        )
        self.keys_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.keys_text.config(state="disabled")

        self._keys_placeholder()

    def _keys_placeholder(self):
        self.keys_text.config(state="normal")
        self.keys_text.delete("1.0", "end")
        self.keys_text.insert("1.0",
            "  Gere um par de chaves para ver os detalhes aqui.\n\n"
            "  Processo RSA:\n"
            "    1. Escolhe dois primos p e q\n"
            "    2. Calcula n = p × q  (módulo)\n"
            "    3. Calcula φ(n) = (p-1)(q-1)  (Totiente de Euler)\n"
            "    4. Escolhe e = 65537  (primo de Fermat)\n"
            "    5. Calcula d = e⁻¹ mod φ(n)  (Euclides Estendido)\n"
        )
        self.keys_text.config(state="disabled")

    def _generate_keys(self):
        bits = int(self.bits_var.get())
        self.btn_gen.config(state="disabled", text="Gerando...")
        self.key_status.config(text="Aguarde…", fg=WARNING)
        self.progress.pack(pady=4)
        self.progress.start(10)

        def worker():
            try:
                pub, priv, p, q, phi_n = generate_keys(bits=bits)
                self.pub_key  = pub
                self.priv_key = priv
                self.after(0, lambda: self._on_keys_ready(pub, priv, p, q, phi_n))
            except Exception as exc:
                self.after(0, lambda: self._on_keys_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_keys_ready(self, pub, priv, p, q, phi_n):
        e, n = pub
        d, _ = priv
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_gen.config(state="normal", text="Gerar Par de Chaves")
        self.key_status.config(text="✔ Chaves prontas!", fg=SUCCESS)
        self._set_status("Par de chaves RSA gerado com sucesso.", SUCCESS)

        info = (
            f"{'─'*60}\n"
            f"  p (primo)   = {p}\n\n"
            f"  q (primo)   = {q}\n\n"
            f"  n = p × q   = {n}\n\n"
            f"  φ(n)        = {phi_n}\n"
            f"{'─'*60}\n"
            f"  CHAVE PÚBLICA  (e, n)\n"
            f"    e = {e}\n"
            f"    n = {n}\n\n"
            f"  CHAVE PRIVADA  (d, n)\n"
            f"    d = {d}\n"
            f"    n = {n}\n"
            f"{'─'*60}\n"
        )
        self.keys_text.config(state="normal")
        self.keys_text.delete("1.0", "end")
        self.keys_text.insert("1.0", info)
        self.keys_text.config(state="disabled")

    def _on_keys_error(self, msg):
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_gen.config(state="normal", text="Gerar Par de Chaves")
        self.key_status.config(text="Erro!", fg="#ff4444")
        messagebox.showerror("Erro ao gerar chaves", msg)

    # ── Aba: Cifrar ─────────────────────────────────────────────────
    def _build_tab_encrypt(self):
        tab = self.tab_encrypt

        tk.Label(tab, text="Mensagem original", font=FONT_B,
                 bg=BG, fg=SUBTEXT).pack(anchor="w", padx=16, pady=(12, 2))

        self.enc_input = scrolledtext.ScrolledText(
            tab, height=6, wrap="word", font=FONT, bg=ENTRY_BG, fg=TEXT,
            insertbackground=TEXT, bd=0, relief="flat",
            highlightthickness=1, highlightbackground=ACCENT
        )
        self.enc_input.pack(fill="x", padx=12, pady=(0, 8))

        # Barra de botões
        bbar = tk.Frame(tab, bg=BG)
        bbar.pack(fill="x", padx=12, pady=4)

        self.btn_enc = tk.Button(
            bbar, text="🔒  Cifrar", font=FONT_B,
            bg=HIGHLIGHT, fg="#ffffff", activebackground="#c73652",
            relief="flat", padx=20, pady=6, cursor="hand2",
            command=self._do_encrypt
        )
        self.btn_enc.pack(side="left")

        tk.Button(
            bbar, text="Limpar", font=FONT,
            bg=ACCENT, fg=TEXT, activebackground="#1c4080",
            relief="flat", padx=12, pady=6, cursor="hand2",
            command=self._clear_encrypt
        ).pack(side="left", padx=8)

        tk.Button(
            bbar, text="Enviar para Decifrar →", font=FONT,
            bg=ACCENT, fg=SUCCESS, activebackground="#1c4080",
            relief="flat", padx=12, pady=6, cursor="hand2",
            command=self._send_to_decrypt
        ).pack(side="right")

        tk.Label(tab, text="Texto cifrado (blocos separados por vírgula)",
                 font=FONT_B, bg=BG, fg=SUBTEXT).pack(anchor="w", padx=16, pady=(8, 2))

        self.enc_output = scrolledtext.ScrolledText(
            tab, height=10, wrap="word", font=MONO, bg=ENTRY_BG, fg=SUCCESS,
            insertbackground=TEXT, bd=0, relief="flat",
            highlightthickness=1, highlightbackground=ACCENT
        )
        self.enc_output.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.enc_output.config(state="disabled")

    def _do_encrypt(self):
        if not self.pub_key:
            messagebox.showwarning("Sem chave", "Gere um par de chaves na aba 'Chaves' primeiro.")
            return
        msg = self.enc_input.get("1.0", "end").strip()
        if not msg:
            messagebox.showwarning("Mensagem vazia", "Digite uma mensagem para cifrar.")
            return
        try:
            self.cipher_blocks = encrypt(msg, self.pub_key)
            result = ", ".join(str(c) for c in self.cipher_blocks)
            self.enc_output.config(state="normal")
            self.enc_output.delete("1.0", "end")
            self.enc_output.insert("1.0", result)
            self.enc_output.config(state="disabled")
            self._set_status(f"Mensagem cifrada em {len(self.cipher_blocks)} bloco(s).", SUCCESS)
        except Exception as exc:
            messagebox.showerror("Erro ao cifrar", str(exc))

    def _clear_encrypt(self):
        self.enc_input.delete("1.0", "end")
        self.enc_output.config(state="normal")
        self.enc_output.delete("1.0", "end")
        self.enc_output.config(state="disabled")
        self.cipher_blocks = []

    def _send_to_decrypt(self):
        raw = self.enc_output.get("1.0", "end").strip()
        if not raw:
            messagebox.showinfo("Vazio", "Cifre uma mensagem primeiro.")
            return
        self.dec_input.config(state="normal")
        self.dec_input.delete("1.0", "end")
        self.dec_input.insert("1.0", raw)
        # Navega para a aba Decifrar
        self.nametowidget(self.winfo_children()[1]).select(2)
        self._set_status("Blocos copiados para a aba Decifrar.", SUCCESS)

    # ── Aba: Decifrar ────────────────────────────────────────────────
    def _build_tab_decrypt(self):
        tab = self.tab_decrypt

        tk.Label(tab, text="Blocos cifrados (separados por vírgula)",
                 font=FONT_B, bg=BG, fg=SUBTEXT).pack(anchor="w", padx=16, pady=(12, 2))

        self.dec_input = scrolledtext.ScrolledText(
            tab, height=8, wrap="word", font=MONO, bg=ENTRY_BG, fg=WARNING,
            insertbackground=TEXT, bd=0, relief="flat",
            highlightthickness=1, highlightbackground=ACCENT
        )
        self.dec_input.pack(fill="x", padx=12, pady=(0, 8))

        bbar = tk.Frame(tab, bg=BG)
        bbar.pack(fill="x", padx=12, pady=4)

        self.btn_dec = tk.Button(
            bbar, text="🔓  Decifrar", font=FONT_B,
            bg=HIGHLIGHT, fg="#ffffff", activebackground="#c73652",
            relief="flat", padx=20, pady=6, cursor="hand2",
            command=self._do_decrypt
        )
        self.btn_dec.pack(side="left")

        tk.Button(
            bbar, text="Limpar", font=FONT,
            bg=ACCENT, fg=TEXT, activebackground="#1c4080",
            relief="flat", padx=12, pady=6, cursor="hand2",
            command=self._clear_decrypt
        ).pack(side="left", padx=8)

        tk.Label(tab, text="Mensagem decifrada", font=FONT_B,
                 bg=BG, fg=SUBTEXT).pack(anchor="w", padx=16, pady=(8, 2))

        self.dec_output = scrolledtext.ScrolledText(
            tab, height=10, wrap="word", font=FONT, bg=ENTRY_BG, fg=TEXT,
            insertbackground=TEXT, bd=0, relief="flat",
            highlightthickness=1, highlightbackground=ACCENT
        )
        self.dec_output.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.dec_output.config(state="disabled")

    def _do_decrypt(self):
        if not self.priv_key:
            messagebox.showwarning("Sem chave", "Gere um par de chaves na aba 'Chaves' primeiro.")
            return
        raw = self.dec_input.get("1.0", "end").strip()
        if not raw:
            messagebox.showwarning("Sem blocos", "Cole os blocos cifrados no campo acima.")
            return
        try:
            blocks = [int(x.strip()) for x in raw.split(",") if x.strip()]
            result = decrypt(blocks, self.priv_key)
            self.dec_output.config(state="normal")
            self.dec_output.delete("1.0", "end")
            self.dec_output.insert("1.0", result)
            self.dec_output.config(state="disabled")
            self._set_status("Mensagem decifrada com sucesso.", SUCCESS)
        except Exception as exc:
            messagebox.showerror("Erro ao decifrar", str(exc))

    def _clear_decrypt(self):
        self.dec_input.delete("1.0", "end")
        self.dec_output.config(state="normal")
        self.dec_output.delete("1.0", "end")
        self.dec_output.config(state="disabled")

    # ── Barra de status ──────────────────────────────────────────────
    def _build_status(self):
        bar = tk.Frame(self, bg=ACCENT, pady=3)
        bar.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="Pronto.")
        tk.Label(bar, textvariable=self.status_var, font=("Segoe UI", 9),
                 bg=ACCENT, fg=SUBTEXT, anchor="w", padx=10).pack(fill="x")

    def _set_status(self, msg: str, color: str = SUBTEXT):
        self.status_var.set(msg)
        # Atualiza a cor do label de status
        bar = self.winfo_children()[-1]           # último filho = barra de status
        bar.winfo_children()[0].config(fg=color)


if __name__ == "__main__":
    app = RSAApp()
    app.mainloop()
