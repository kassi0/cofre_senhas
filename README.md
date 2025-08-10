# Cofre de Senhas

Um gerenciador de senhas simples, offline e multiplataforma, com interface **CustomTkinter** e armazenamento em **SQLite**. Ideal para uso pessoal/local.

## ✨ Funcionalidades

* **Senha Mestra** (hash com `bcrypt`) para liberar o app
* **Cadastro rápido** de pares **Serviço** + **Senha**
* **Gerador de senhas** com opções:

  * Tamanho ajustável (4–64)
  * Incluir **maiúsculas**, **minúsculas**, **números** e **símbolos**
* **Copiar** senha para a área de transferência (com fallback se `pyperclip` falhar)
* **Listagem** com rolagem, máscara de senha e ações **Copiar** / **Excluir**
* **Exportar CSV**
* **Alterar Senha Mestra**
* **Escolher arquivo do banco (.db)** e persistir no `config.json`
* Ícone da janela: tenta **.ico** (Windows) e cai para **.png** (Linux/macOS)

## 🧱 Tecnologias / Bibliotecas

* **Python 3.10+**
* **CustomTkinter** (UI moderna sobre Tkinter)
* **bcrypt** (hash de senha mestra)
* **sqlite3** (nativo do Python)
* **pyperclip** (opcional; usamos fallback do Tk se indisponível)
* **Pillow** (para `iconphoto` com PNG)

### `requirements.txt`

```txt
bcrypt
pyperclip
customtkinter
pillow
```

> Observação: `sqlite3` já vem na biblioteca padrão do Python.

## 🗂️ Estrutura sugerida

```
cofre-senhas/
├─ appCT.py                # arquivo principal (CustomTkinter)
├─ requirements.txt
├─ icone.ico               # ícone (Windows)
├─ icone.png               # ícone (Linux/macOS)
└─ config.json             # gerado em runtime (db_path, prefs)
```

## ⚙️ Configuração

* **Banco de dados**: por padrão, `cofredb.db` no diretório do app. Você pode trocar em **Banco de Dados** → escolhe/gera outro `.db`. O caminho fica salvo em `config.json`.
* **Senha mestra**: na primeira execução, o app pedirá para definir. É salva apenas o **hash** `bcrypt`.
* **Ícone**: no `__init__` do app há uma lógica que tenta `iconbitmap(icone.ico)` e, se falhar, usa `iconphoto(icone.png)` via Pillow.

## ▶️ Como usar (dev)

1. Crie e ative um ambiente virtual

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```
2. Instale dependências

   ```bash
   pip install -r requirements.txt
   ```
3. Rode o app

   ```bash
   python appCT.py
   ```

## 🧪 Fluxo básico

1. **Defina a senha mestra** (primeira vez)
2. **Cadastre**: informe *Nome do Serviço* e *Senha* (ou **Gere** uma senha com as opções desejadas)
3. Use **Copiar** para mandar a senha pro clipboard
4. Em **Banco de Dados**, você pode mudar o arquivo `.db`
5. **Exportar CSV** para backup/visualização

## 🧰 Compilar para Windows (.exe)

Usando **PyInstaller**. *Não existe cross-compile*: gere o `.exe` no Windows.

### Instalar PyInstaller

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
```

### Gerar .exe (onefile, sem console)

```powershell
pyinstaller appCT.py `
  --name CofreSenhas-CTK `
  --onefile --noconsole `
  --icon icone.ico `
  --add-data "icone.png;."
```

Saída em `dist/CofreSenhas-CTK.exe`.

> **Notas**
>
> * No Windows, o separador de `--add-data` é `;`.
> * Incluímos o `icone.png` para garantir o ícone em ambientes não-Windows.

### (Opcional) Arquivo `.spec`

Crie `cofre_ctk.spec` para builds repetíveis:

```python
# cofre_ctk.spec
# use: pyinstaller cofre_ctk.spec

a = Analysis(
    ['appCT.py'],
    pathex=['.'],
    datas=[('icone.png','.')],
    binaries=[],
    hiddenimports=[],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts,
    name='CofreSenhas-CTK',
    icon='icone.ico',
    console=False,
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas,
               strip=False, upx=False, name='CofreSenhas-CTK')
```

Rode:

```powershell
pyinstaller cofre_ctk.spec
```

## 🐧 Linux e 🍎 macOS (execução)

O projeto é **multiplataforma** (Tkinter). Para distribuir binário nesses sistemas, você pode usar PyInstaller neles também:

```bash
pyinstaller appCT.py \
  --name CofreSenhas-CTK \
  --onefile --noconsole \
  --icon icone.ico \
  --add-data "icone.png:."
```

> No Linux/macOS o separador de `--add-data` é `:`. O binário sai em `dist/`.

## 🩹 Dicas & Troubleshooting

* **Clipboard no Linux**: se `pyperclip` não achar backend, o app usa **fallback do Tk** (`clipboard_append`). Nada pra fazer.
* **Ícone não aparece**: confirme que `icone.png` está sendo incluído e que o código chama `iconphoto`. Com PyInstaller, garanta `--add-data` correto.
* **DB travado**: feche instâncias duplicadas do app antes de editar o `.db` manualmente.
* **Letreiro cortado/estilo**: a janela é redimensionável; a tabela ocupa todo o espaço e os botões ficam à direita sem esmagar texto.

## 🔐 Segurança

* As senhas ficam em **texto** no banco (para permitir copiar). A proteção principal é o **acesso físico** ao arquivo + a **senha mestra** para abrir o app. Para maior segurança, use um volume criptografado do SO.

## 📜 Licença

MIT License

Copyright (c) 2025 Cássio Telles

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**Quer contribuir?** Pull Requests são bem-vindos. Abra uma issue com melhorias/bugs.
