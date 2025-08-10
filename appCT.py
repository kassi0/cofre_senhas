import os
import json
import csv
import bcrypt
import sqlite3
import string
import secrets
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

DB_DEFAULT = "cofredb.db"
CONFIG_FILE = "config.json"
ICON_FILE = "icone.ico"


def get_banco_path():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('db_path', DB_DEFAULT)
        except Exception:
            return DB_DEFAULT
    return DB_DEFAULT


def set_banco_path(path):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({"db_path": path}, f, ensure_ascii=False, indent=2)


def escolher_banco():
    filename = filedialog.asksaveasfilename(
        defaultextension=".db",
        filetypes=[("SQLite DB", "*.db"), ("Todos arquivos", "*.*")]
    )
    if filename:
        set_banco_path(filename)
        return filename
    return None


def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS senha_mestra (id INTEGER PRIMARY KEY, hash BLOB NOT NULL);""")
    cur.execute("""CREATE TABLE IF NOT EXISTS senhas (id INTEGER PRIMARY KEY AUTOINCREMENT, servico TEXT NOT NULL, senha   TEXT NOT NULL);""")
    conn.commit(); conn.close()


def senha_mestra_existe(db_path):
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM senha_mestra"); existe = cur.fetchone()[0] > 0
    conn.close(); return existe


def salvar_senha_mestra(db_path, senha):
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    hashpw = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    cur.execute("DELETE FROM senha_mestra")
    cur.execute("INSERT INTO senha_mestra(hash) VALUES (?)", (hashpw,))
    conn.commit(); conn.close()


def validar_senha_mestra(db_path, senha):
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("SELECT hash FROM senha_mestra LIMIT 1"); row = cur.fetchone()
    conn.close();
    if not row: return False
    hashpw = row[0]
    try:
        return bcrypt.checkpw(senha.encode(), hashpw)
    except Exception:
        if isinstance(hashpw, str):
            return bcrypt.checkpw(senha.encode(), hashpw.encode())
        return False


def atualizar_senha_mestra(db_path, nova):
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    hashpw = bcrypt.hashpw(nova.encode(), bcrypt.gensalt())
    cur.execute("UPDATE senha_mestra SET hash=?", (hashpw,))
    conn.commit(); conn.close()


def salvar_senha(db_path, servico, senha):
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("INSERT INTO senhas(servico, senha) VALUES (?,?)", (servico, senha))
    conn.commit(); conn.close()


def listar_senhas(db_path):
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("SELECT id, servico, senha FROM senhas ORDER BY servico COLLATE NOCASE")
    rows = cur.fetchall(); conn.close(); return rows


def excluir_senha_db(db_path, row_id):
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("DELETE FROM senhas WHERE id=?", (row_id,))
    conn.commit(); conn.close()


def gerar_senha(tamanho=16, usar_maiusculas=True, usar_minusculas=True, usar_numeros=True, usar_simbolos=True):
    alphabet = ""
    if usar_minusculas: alphabet += string.ascii_lowercase
    if usar_maiusculas: alphabet += string.ascii_uppercase
    if usar_numeros:    alphabet += string.digits
    if usar_simbolos:   alphabet += "!@#$%^&*()-_=+[]{};:,.?/"
    if not alphabet:    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(tamanho))


def copy_to_clipboard_tk(widget, text: str) -> bool:
    try:
        import pyperclip; pyperclip.copy(text); return True
    except Exception:
        pass
    try:
        widget.clipboard_clear(); widget.clipboard_append(text); widget.update(); return True
    except Exception:
        return False


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Cofre de Senhas")
        self.geometry("1100x650")
        self.minsize(980, 580)

        # --- Ícone: tenta .ico (Windows) e cai para .png (Linux/macOS) ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(base_dir, "icone.ico")
        png_path = os.path.join(base_dir, "icone.png")

        # 1) .ico (melhor no Windows)
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

        # 2) .png (Wayland/X11/macOS/funciona no Windows também)
        if os.path.exists(png_path):
            try:
                img = Image.open(png_path)
                self._icon_img = ImageTk.PhotoImage(img)  # mantém referência
                self.iconphoto(True, self._icon_img)
            except Exception:
                pass
        # --- fim ícone ---

        self.db_path = get_banco_path(); init_db(self.db_path)

        # layout principal
        self.sidebar = ctk.CTkFrame(self, width=220); self.sidebar.pack(side="left", fill="y")
        self.main    = ctk.CTkFrame(self);            self.main.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self._montar_sidebar()
        if not senha_mestra_existe(self.db_path): self._tela_cadastrar_mestra()
        else:                                       self._tela_login()

    def _montar_sidebar(self):
        ctk.CTkLabel(self.sidebar, text="Cofre", font=("Segoe UI", 22, "bold")).pack(pady=(20,10))
        ctk.CTkButton(self.sidebar, text="Principal", command=self._tela_principal).pack(pady=6, fill="x", padx=10)
        ctk.CTkButton(self.sidebar, text="Alterar Mestra", command=self._tela_alterar_mestra).pack(pady=6, fill="x", padx=10)
        ctk.CTkButton(self.sidebar, text="Banco de Dados", command=self._abrir_config).pack(pady=6, fill="x", padx=10)
        self.lbl_db = ctk.CTkLabel(self.sidebar, text=f"DB: {os.path.basename(self.db_path)}", wraplength=180)
        self.lbl_db.pack(pady=(20,5), padx=10)

    def _limpar_main(self):
        for w in self.main.winfo_children(): w.destroy()

    def _tela_login(self):
        self._limpar_main()
        ctk.CTkLabel(self.main, text="Digite a Senha Mestra", font=("Segoe UI", 18, "bold")).pack(pady=(30,10))
        self.senha_login_var = ctk.StringVar()
        entry = ctk.CTkEntry(self.main, show="*", textvariable=self.senha_login_var, width=340); entry.pack(pady=10); entry.focus_set()
        ctk.CTkButton(self.main, text="Entrar", command=lambda: (self._tela_principal() if validar_senha_mestra(self.db_path, self.senha_login_var.get()) else messagebox.showerror("Erro","Senha mestra incorreta"))).pack(pady=10)

    def _tela_cadastrar_mestra(self):
        self._limpar_main()
        ctk.CTkLabel(self.main, text="Crie a Senha Mestra", font=("Segoe UI", 18, "bold")).pack(pady=(30,10))
        s1 = ctk.StringVar(); s2 = ctk.StringVar()
        ctk.CTkEntry(self.main, show='*', placeholder_text="Senha", textvariable=s1, width=340).pack(pady=6)
        ctk.CTkEntry(self.main, show='*', placeholder_text="Confirme", textvariable=s2, width=340).pack(pady=6)
        def cadastrar():
            if not s1.get(): return messagebox.showwarning("Aviso","Informe uma senha")
            if s1.get()!=s2.get(): return messagebox.showwarning("Aviso","Senhas diferentes")
            salvar_senha_mestra(self.db_path, s1.get()); messagebox.showinfo("OK","Senha mestra cadastrada!"); self._tela_principal()
        ctk.CTkButton(self.main, text="Salvar", command=cadastrar).pack(pady=12)

    def _tela_alterar_mestra(self):
        self._limpar_main()
        ctk.CTkLabel(self.main, text="Alterar Senha Mestra", font=("Segoe UI", 18, "bold")).pack(pady=(30,10))
        atual = ctk.StringVar(); nova = ctk.StringVar(); conf = ctk.StringVar()
        ctk.CTkEntry(self.main, show='*', placeholder_text="Atual", textvariable=atual, width=340).pack(pady=6)
        ctk.CTkEntry(self.main, show='*', placeholder_text="Nova", textvariable=nova, width=340).pack(pady=6)
        ctk.CTkEntry(self.main, show='*', placeholder_text="Confirmar", textvariable=conf, width=340).pack(pady=6)
        def alterar():
            if not validar_senha_mestra(self.db_path, atual.get()): return messagebox.showerror("Erro","Senha atual incorreta")
            if not nova.get(): return messagebox.showwarning("Aviso","Nova senha vazia")
            if nova.get()!=conf.get(): return messagebox.showwarning("Aviso","Confirmação não confere")
            atualizar_senha_mestra(self.db_path, nova.get()); messagebox.showinfo("OK","Senha mestra atualizada"); self._tela_principal()
        ctk.CTkButton(self.main, text="Alterar", command=alterar).pack(pady=12)

    def _tela_principal(self):
        self._limpar_main()
        header = ctk.CTkFrame(self.main)
        header.pack(fill="x", pady=(0,6))
        header.grid_columnconfigure(1, weight=1)

        self.servico_var = ctk.StringVar(); self.senha_var = ctk.StringVar()

        # Labels acima dos campos
        ctk.CTkLabel(header, text="Nome do Serviço", font=("Segoe UI", 12, "bold"))\
            .grid(row=0, column=0, padx=(0,8), pady=(8,0), sticky="w")
        ctk.CTkLabel(header, text="Senha Gerada", font=("Segoe UI", 12, "bold"))\
            .grid(row=0, column=1, padx=(0,8), pady=(8,0), sticky="w")

        # Campos
        ctk.CTkEntry(header, placeholder_text="Serviço (ex: Gmail)", textvariable=self.servico_var, width=320)\
            .grid(row=1, column=0, padx=(0,8), pady=(2,8), sticky="w")
        ctk.CTkEntry(header, placeholder_text="Senha", textvariable=self.senha_var)\
            .grid(row=1, column=1, padx=(0,8), pady=(2,8), sticky="ew")

        # Botão Salvar alinhado à linha dos campos
        ctk.CTkButton(header, text="Salvar", command=self._salvar_click, width=110)\
            .grid(row=1, column=2, padx=(0,8), pady=(2,8))

        gen = ctk.CTkFrame(self.main); gen.pack(fill="x", pady=(0,8))
        for i in range(6): gen.grid_columnconfigure(i, weight=0)
        gen.grid_columnconfigure(5, weight=1)
        ctk.CTkLabel(gen, text="Tamanho:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.len_slider = ctk.CTkSlider(gen, from_=4, to=64, number_of_steps=60); self.len_slider.set(16)
        self.len_slider.grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self.len_val = ctk.CTkLabel(gen, text="16"); self.len_val.grid(row=0, column=2, padx=6, pady=6)
        self.len_slider.configure(command=lambda v: self.len_val.configure(text=str(int(v))))
        self.cb_upper = ctk.CTkCheckBox(gen, text="Maiúsculas"); self.cb_upper.select(); self.cb_upper.grid(row=0, column=3, padx=6, pady=6)
        self.cb_lower = ctk.CTkCheckBox(gen, text="Minúsculas"); self.cb_lower.select(); self.cb_lower.grid(row=0, column=4, padx=6, pady=6)
        self.cb_digits = ctk.CTkCheckBox(gen, text="Números"); self.cb_digits.select(); self.cb_digits.grid(row=1, column=3, padx=6, pady=6)
        self.cb_symbols = ctk.CTkCheckBox(gen, text="Símbolos"); self.cb_symbols.select(); self.cb_symbols.grid(row=1, column=4, padx=6, pady=6)
        ctk.CTkButton(gen, text="Gerar senha", command=self._gerar_click).grid(row=0, column=5, rowspan=2, padx=8, pady=6, sticky="e")

        # Tabela ocupando TUDO
        table_frame = ctk.CTkFrame(self.main); table_frame.pack(fill="both", expand=True, pady=(8,8))
        self.lista = ctk.CTkScrollableFrame(table_frame)
        self.lista.pack(fill="both", expand=True)
        # chave: deixar a coluna 0 da scrollframe com peso -> linhas esticam
        self.lista.grid_columnconfigure(0, weight=1)

        head = ctk.CTkFrame(self.lista)
        head.grid(row=0, column=0, sticky="ew", padx=4, pady=(0,6))
        head.grid_columnconfigure(0, weight=1)
        head.grid_columnconfigure(1, weight=1)
        head.grid_columnconfigure(2, weight=0)
        ctk.CTkLabel(head, text="Serviço", anchor="w").grid(row=0, column=0, padx=6, sticky="w")
        ctk.CTkLabel(head, text="Senha",   anchor="w").grid(row=0, column=1, padx=6, sticky="w")
        ctk.CTkLabel(head, text="Ações",   anchor="center").grid(row=0, column=2, padx=6)

        self._popular_lista()

        footer = ctk.CTkFrame(self.main); footer.pack(fill="x")
        ctk.CTkButton(footer, text="Exportar CSV", command=self._exportar_csv).pack(side="left", padx=(0,6))
        ctk.CTkButton(footer, text="Atualizar",   command=self._popular_lista).pack(side="left")

    def _popular_lista(self):
        for child in self.lista.winfo_children():
            if child is not None and child.grid_info().get('row', 0) != 0: child.destroy()
        rows = listar_senhas(self.db_path)
        for i, (row_id, servico, senha) in enumerate(rows, start=1):
            linha = ctk.CTkFrame(self.lista)
            linha.grid(row=i, column=0, sticky="ew", padx=4, pady=2)
            linha.grid_columnconfigure(0, weight=1)
            linha.grid_columnconfigure(1, weight=1)
            linha.grid_columnconfigure(2, weight=0)
            ctk.CTkLabel(linha, text=servico, anchor="w").grid(row=0, column=0, padx=6, sticky="ew")
            mask = "•" * min(len(senha), 12)
            ctk.CTkLabel(linha, text=mask, anchor="w").grid(row=0, column=1, padx=6, sticky="ew")
            acoes = ctk.CTkFrame(linha); acoes.grid(row=0, column=2, padx=6, sticky="e")
            def make_copy(s=senha):
                return lambda: (copy_to_clipboard_tk(self, s), messagebox.showinfo("Copiado", "Senha copiada"))
            ctk.CTkButton(acoes, text="Copiar", width=74, command=make_copy()).pack(side="left", padx=(0,6))
            ctk.CTkButton(acoes, text="Excluir", width=74, fg_color="#b91c1c", hover_color="#991b1b",
                          command=lambda rid=row_id: self._excluir(rid)).pack(side="left")

    def _gerar_click(self):
        tamanho = int(self.len_slider.get())
        usar_maiusculas = bool(self.cb_upper.get()); usar_minusculas = bool(self.cb_lower.get())
        usar_numeros = bool(self.cb_digits.get());  usar_simbolos   = bool(self.cb_symbols.get())
        self.senha_var.set(gerar_senha(tamanho, usar_maiusculas, usar_minusculas, usar_numeros, usar_simbolos))

    def _salvar_click(self):
        servico = self.servico_var.get().strip(); senha = self.senha_var.get().strip()
        if not servico or not senha: return messagebox.showwarning("Aviso","Preencha serviço e senha")
        salvar_senha(self.db_path, servico, senha); self.servico_var.set(""); self.senha_var.set(""); self._popular_lista()

    def _excluir(self, row_id):
        if messagebox.askyesno("Confirmar","Excluir este registro?"):
            excluir_senha_db(self.db_path, row_id); self._popular_lista()

    def _exportar_csv(self):
        fname = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not fname: return
        rows = listar_senhas(self.db_path)
        with open(fname,'w',newline='',encoding='utf-8') as f:
            writer = csv.writer(f); writer.writerow(["id","servico","senha"])
            for r in rows: writer.writerow(r)
        messagebox.showinfo("OK","CSV exportado!")

    def _abrir_config(self):
        top = ctk.CTkToplevel(self); top.title("Configurações"); top.geometry("480x240")
        ctk.CTkLabel(top, text="Banco de Dados", font=("Segoe UI", 16, "bold")).pack(pady=(14,8))
        ctk.CTkLabel(top, text=f"Atual: {self.db_path}", wraplength=420).pack(pady=(0,8))
        def escolher():
            novo = escolher_banco()
            if novo:
                self.db_path = novo; init_db(self.db_path)
                self.lbl_db.configure(text=f"DB: {os.path.basename(self.db_path)}"); messagebox.showinfo("OK","Banco configurado!")
        ctk.CTkButton(top, text="Escolher/Alterar arquivo .db", command=escolher).pack(pady=8)


if __name__ == "__main__":
    app = App(); app.mainloop()
