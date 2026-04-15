# ⬡ Fortis — Local Encrypted Password Manager

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Encryption](https://img.shields.io/badge/Encryption-AES--256--GCM-gold?style=flat-square)
![UI](https://img.shields.io/badge/UI-CustomTkinter-purple?style=flat-square)

---

## ✦ Features

| Feature | Details |
|--------|---------|
|  **AES-256-GCM encryption** | Industry-standard authenticated encryption |
|  **PBKDF2-SHA256 key derivation** | 390,000 iterations — brute-force resistant |
|  **Modern dark UI** | Built with CustomTkinter, no browser needed |
|  **Auto-clear clipboard** | Password auto-wiped from clipboard after 30s |
|  **Password generator** | Configurable length, charset, and strength meter |
|  **Real-time search** | Instant filtering across name, username, URL |
|  **100% local** | Your data never leaves your machine (`.fortis.vault`) |
|  **No telemetry** | No analytics, no accounts, no cloud |

---

##  Installation

### Prerequisites
- Python 3.10+
- pip

### Steps

```bash
# Clone the repository
git clone https://github.com/AstonDiv1/fortis.git
cd fortis

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

---

##  Security Details

### How your data is protected

```
Master Password
      │
      ▼
 PBKDF2-SHA256 (390,000 iterations + 32-byte random salt)
      │
      ▼
  256-bit AES key
      │
      ▼
  AES-256-GCM (authenticated encryption + random nonce)
      │
      ▼
  .fortis.vault  ← stored in your home directory
```

- **Salt**: 32 bytes, randomly generated once at vault creation
- **Nonce**: 12 bytes, freshly randomized on every save
- **Authentication tag**: GCM mode ensures data integrity (tamper detection)
- **Wrong password?** Decryption fails silently — no hints given to attackers

### Vault file location

| OS | Path |
|----|------|
| Linux / macOS | `~/.fortis.vault` |
| Windows | `C:\Users\<you>\.fortis.vault` |

---

##  Project Structure

```
fortis/
├── main.py              # Entry point
├── requirements.txt
├── README.md
└── fortis/
    ├── __init__.py
    ├── app.py           # Main GUI (CustomTkinter)
    ├── vault.py         # AES-256-GCM encryption logic
    └── generator.py     # Password generator & strength meter
```

---

##  Tech Stack

- **[Python 3.10+](https://python.org)** — core language
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** — modern themed GUI
- **[cryptography](https://cryptography.io)** — AES-256-GCM + PBKDF2 via pyca
- **[pyperclip](https://github.com/asweigart/pyperclip)** — clipboard access

---

##  License

MIT — free to use, modify, and distribute.

---

<p align="center">
  Built with Python · No cloud · No tracking · Just your keys.
</p>
