# 🔐 InfoSec Secure Banking System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Cryptography](https://img.shields.io/badge/Cryptography-PyCryptodome-red?style=for-the-badge&logo=lock&logoColor=white)
![Blockchain](https://img.shields.io/badge/Blockchain-PoW-orange?style=for-the-badge&logo=bitcoin&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A comprehensive blockchain-based secure banking platform implementing multiple cryptographic algorithms**

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Cryptography](#-cryptography) • [Demo](#-demo)

</div>

---

## 📋 Overview

The **InfoSec Secure Banking System** is a full-featured Python banking platform that demonstrates practical implementation of information security concepts. It combines **blockchain technology** with **robust cryptographic protocols** to ensure secure, transparent, and tamper-proof financial transactions.

```
╔══════════════════════════════════════════════════════════╗
║   🔐  INFOSEC SECURE BANKING SYSTEM  🔐                   ║
║   RSA • AES • DH • Blockchain • Digital Signatures       ║
╚══════════════════════════════════════════════════════════╝
```

---

## ✨ Features

### 🔒 Security Features
| Feature | Implementation | Description |
|---------|---------------|-------------|
| **Asymmetric Encryption** | RSA-2048/4096 | Digital signatures & key encryption |
| **Symmetric Encryption** | AES-256-CBC | Data protection & wallet encryption |
| **Key Exchange** | Diffie-Hellman | Secure session key establishment |
| **Hybrid Encryption** | AES + RSA | Transaction memo protection |
| **Hash-Based Signatures** | Lamport | Quantum-resistant security |
| **PKI** | X.509 Certificates | Identity verification |

### 🏦 Banking Features
- ✅ Secure wallet creation with password protection
- ✅ Certificate Authority (CA) for identity management
- ✅ Encrypted money transfers between users
- ✅ Real-time balance tracking
- ✅ Blockchain-based transaction ledger
- ✅ Proof-of-Work mining
- ✅ Chain integrity verification

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Banking    │    │    Wallet    │    │   Display    │       │
│  │    Client    │◄──►│   Manager    │    │    Utils     │       │
│  └──────┬───────┘    └──────────────┘    └──────────────┘       │
│         │                                                        │
├─────────┼────────────────────────────────────────────────────────┤
│         │              CRYPTO LAYER                              │
├─────────┼────────────────────────────────────────────────────────┤
│         ▼                                                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │     RSA      │    │     AES      │    │   Diffie-    │       │
│  │   Manager    │    │   Manager    │    │   Hellman    │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   ElGamal    │    │   Lamport    │    │ Certificate  │       │
│  │  Encryption  │    │  Signatures  │    │   Manager    │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                        SERVER LAYER                              │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Banking    │    │ Certificate  │    │  Blockchain  │       │
│  │    Server    │◄──►│  Authority   │◄──►│    Ledger    │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                        DATA LAYER                                │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Storage    │    │    Wallet    │    │    Audit     │       │
│  │   Manager    │    │   Keystore   │    │     Logs     │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
└──────────────────────────────────────────────────────────────────┘
```

### Transaction Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Create  │────►│  Encrypt │────►│   Sign   │────►│  Submit  │
│Transaction│    │   Memo   │     │    TX    │     │ to Server│
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                         │
                                                         ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   Done   │◄────│   Mine   │◄────│  Check   │◄────│  Verify  │
│    ✓     │     │  Block   │     │ Balance  │     │Signature │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

### Hybrid Encryption Process

```
                    ┌─────────────────┐
                    │  Plaintext Memo │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                              ▼
     ┌─────────────────┐           ┌─────────────────┐
     │ Random AES Key  │           │ Recipient's RSA │
     │    (256-bit)    │           │   Public Key    │
     └────────┬────────┘           └────────┬────────┘
              │                              │
              ▼                              ▼
     ┌─────────────────┐           ┌─────────────────┐
     │  AES-256-CBC    │           │    RSA-OAEP     │
     │   Encryption    │           │   Encryption    │
     └────────┬────────┘           └────────┬────────┘
              │                              │
              ▼                              ▼
     ┌─────────────────┐           ┌─────────────────┐
     │ Encrypted Memo  │           │ Encrypted Key   │
     └─────────────────┘           └─────────────────┘
```

---

## 📦 Project Structure

```
infosec_banking/
├── 📁 core/
│   ├── client.py          # Banking client with UI
│   └── server.py          # Multi-threaded banking server
│
├── 📁 crypto/
│   ├── rsa_manager.py     # RSA encryption & signatures
│   ├── crypto_manager.py  # AES-256-CBC encryption
│   ├── diffie_hellman.py  # DH key exchange
│   ├── elgamal.py         # ElGamal encryption
│   ├── lamport.py         # Quantum-resistant signatures
│   ├── ca.py              # Certificate Authority
│   └── certificate.py     # X.509 style certificates
│
├── 📁 models/
│   ├── blockchain.py      # Blockchain with PoW
│   ├── block.py           # Block structure
│   ├── transaction.py     # Signed transactions
│   └── wallet.py          # Encrypted wallet storage
│
├── 📁 storage/
│   └── storage_manager.py # Atomic JSON operations
│
├── 📁 utils/
│   ├── display.py         # ASCII UI helpers
│   └── colors.py          # Terminal colors
│
├── 📁 data/                # Runtime data (auto-generated)
│   ├── keystore/          # User wallets
│   ├── certificates.json  # Issued certificates
│   └── ledger.json        # Blockchain
│
├── main.py                # Main application entry
└── config.py              # Configuration
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/HasnatKhan010/INFO-SEC-PROJECT.git
cd INFO-SEC-PROJECT

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install pycryptodome
```

---

## 🎮 Usage

### Start the Server
```bash
# Terminal 1
python -m infosec_banking.core.server
```

**Expected Output:**
```
╔══════════════════════════════════════════════════════════╗
║   🏦  INFOSEC BANKING SERVER  🏦                        ║
╚══════════════════════════════════════════════════════════╝
[12:00:00] ✓ Listening on 127.0.0.1:5005
[12:00:00] → Blockchain: 1 blocks
[12:00:00] → Registered users: 0
```

### Start the Client
```bash
# Terminal 2
python main.py
```

### Workflow

1. **Create Wallet** → Generate RSA keys, encrypt with password
2. **Register with CA** → Get digital certificate, receive $1000
3. **Send Money** → Enter recipient, amount, memo
4. **View Blockchain** → See all transaction blocks
5. **Verify Chain** → Check blockchain integrity

---

## 🔐 Cryptography

### Algorithms Implemented

| Algorithm | Type | Key Size | Usage |
|-----------|------|----------|-------|
| **RSA** | Asymmetric | 2048/4096-bit | Signatures, Key encryption |
| **AES** | Symmetric | 256-bit | Data encryption |
| **SHA-256** | Hash | 256-bit | Hashing, PoW |
| **Diffie-Hellman** | Key Exchange | 2048-bit | Session keys |
| **ElGamal** | Asymmetric | 2048-bit | Encryption (DLP-based) |
| **Lamport** | Hash-based | 256-bit | Quantum-resistant sigs |

### Security Properties

- ✅ **Confidentiality** - AES-256 + RSA encryption
- ✅ **Integrity** - SHA-256 blockchain hashing
- ✅ **Authentication** - PKI certificates
- ✅ **Non-repudiation** - RSA digital signatures
- ✅ **Forward Secrecy** - Diffie-Hellman exchange

---

## 🎬 Demo

### Sample Transaction

```
  ▶ TRANSACTION CREATION
    ├─ Transaction ID: a1b2c3d4
    ✓ Transaction created

  ▶ HYBRID ENCRYPTION (AES + RSA)
    ├─ Generating AES-256 session key...
    ├─ Encrypting memo with AES-256-CBC...
    ├─ Encrypting AES key with recipient's RSA public key...
    ✓ Encryption complete

  ▶ DIGITAL SIGNATURE
    ├─ Hashing transaction with SHA-256...
    ├─ Signing with private key (RSA-PKCS#1)...
    ✓ Signature: m4rKsIgNaTuRe...

    ╔═══════════════════════════════════════╗
    ║   TRANSACTION SUCCESSFUL! ✓           ║
    ╚═══════════════════════════════════════╝
```

### Blockchain Verification

```
  ▶ BLOCKCHAIN VERIFICATION
    ├─ Verifying block #1...
    ├─ Verifying block #2...
    ├─ Verifying block #3...
    ✓ All 4 blocks verified!

    ╔═══════════════════════════════════════╗
    ║   BLOCKCHAIN VALID! ✓                 ║
    ╚═══════════════════════════════════════╝
```

---

## 🧪 Testing

### Test Scenarios

| Test | Status |
|------|--------|
| Wallet Creation with Encryption | ✅ Pass |
| Certificate Issuance by CA | ✅ Pass |
| Money Transfer (End-to-End) | ✅ Pass |
| Invalid Signature Rejection | ✅ Pass |
| Wrong Password Authentication | ✅ Pass |
| Blockchain Integrity Check | ✅ Pass |
| Chain Tampering Detection | ✅ Pass |

---

## 📊 Technical Specifications

| Component | Specification |
|-----------|--------------|
| **Language** | Python 3.8+ |
| **Crypto Library** | PyCryptodome |
| **Network** | TCP Sockets |
| **Serialization** | Pickle + JSON |
| **Blockchain Difficulty** | 2 (hash starts with "00") |
| **RSA User Keys** | 2048-bit |
| **RSA CA Keys** | 4096-bit |
| **AES Mode** | CBC with PKCS7 padding |
| **Hash Function** | SHA-256 |

---

## 👨‍💻 Author

**Hasnat Khan**
- Registration: SP24-BCS-039
- Course: Information Security (Lab Final)
- Instructor: Sabghat Ullah Khan
- Program: BS Computer Science (BCS4A)

---

## 📄 License

This project is developed for educational purposes as part of the Information Security course.

---

## 🙏 Acknowledgments

- PyCryptodome for cryptographic primitives
- RFC 3526 for Diffie-Hellman parameters
- NIST for AES and SHA-256 standards

---

<div align="center">

**⭐ Star this repository if you found it helpful! ⭐**

Made with ❤️ for Information Security

</div>
