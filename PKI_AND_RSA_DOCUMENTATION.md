# PKI and RSA Documentation

## Overview
This document explains the Public Key Infrastructure (PKI) and RSA implementation within the InfoSec Banking System. These components are critical for ensuring **Confidentiality**, **Integrity**, and **Authenticity** of transactions and user data.

---

## 1. RSA (Rivest–Shamir–Adleman)

### What is RSA?
RSA is an asymmetric cryptographic algorithm. Unlike symmetric algorithms (like AES) that use a single key for both encryption and decryption, RSA uses a **Key Pair**:
*   **Public Key**: Shared openly. Used for **Encrypting** messages and **Verifying** signatures.
*   **Private Key**: Kept secret. Used for **Decrypting** messages and **Signing** data.

### Implementation in Project
The RSA logic is encapsulated in `crypto/rsa_manager.py` via the `RSAManager` class.

#### Key Generation
*   **Library**: `pycryptodome`
*   **Key Size**: Defaults to **2048 bits** for standard users, **4096 bits** for the Certificate Authority.
*   **Format**: Keys are exported in PEM format (Privacy Enhanced Mail).

#### Digital Signatures (Integrity & Non-Repudiation)
We use digital signatures to prove that a message originated from a specific user and has not been tampered with.
*   **Algorithm**: **RSASSA-PKCS1-v1_5**
*   **Hashing**: **SHA-256**
    *   Before signing, the data is hashed using SHA-256 to create a fixed-size digest.
    *   This digest is then encrypted with the sender's **Private Key**.
*   **Verification**:
    *   The recipient decrypts the signature using the sender's **Public Key** to reveal the hash.
    *   The recipient independently hashes the received data.
    *   If the two hashes match, the signature is valid.

#### Encryption (Confidentiality)
*   **Algorithm**: **RSA-OAEP** (Optimal Asymmetric Encryption Padding).
*   **Process**:
    *   Data is encrypted using the recipient's **Public Key**.
    *   Only the recipient's **Private Key** can decrypt it.
*   **Usage**: Primarily used for secure key exchange or small data payloads.

---

## 2. PKI (Public Key Infrastructure)

### What is PKI?
PKI is the framework that manages digital keys and certificates. It solves the "Trust" problem: *How do I know this Public Key actually belongs to Alice?*

### Implementation in Project
The PKI system is managed by the `CertificateAuthority` class in `crypto/ca.py`.

#### Components

1.  **Certificate Authority (CA)**
    *   **Role**: The "Root of Trust". It is a trusted entity that issues digital certificates.
    *   **Root Keys**: The CA has its own 4096-bit RSA key pair (`data/ca_key.pem`).
    *   **Function**: It verifies user identities (in a real scenario; here, it binds a User ID to a Key) and signs their public keys.

2.  **Digital Certificates**
    *   **Definition**: A digital document that binds a Public Key to an Identity (User ID).
    *   **Structure** (managed in `crypto/certificate.py`):
        *   `Serial Number`: Unique identifier (UUID).
        *   `Subject`: The owner of the key (e.g., "user_123").
        *   `Issuer`: Who signed this cert (e.g., "InfoSec Bank Root CA").
        *   `Public Key`: The user's RSA Public Key.
        *   `Signature`: The CA's digital signature of the above fields.

#### PKI Workflow

1.  **Initialization**:
    *   The `CertificateAuthority` initializes. If no keys exist, it generates a root key pair.

2.  **Issuance (`issue_certificate`)**:
    *   A user presents their **Public Key** and **User ID** to the CA.
    *   The CA creates a `Certificate` object containing this info.
    *   The CA **signs** the certificate using the **CA Private Key**.
    *   The certificate is stored in `data/certificates.json`.

3.  **Verification (`verify_certificate`)**:
    *   When a user presents a certificate, the system needs to validate it.
    *   The system uses the **CA Public Key** to verify the signature on the certificate.
    *   If valid, the system trusts that the Public Key inside the certificate belongs to the User ID specified in the `Subject`.

---

## 3. How It Works Together (Example Flow)

**Scenario**: User A sends a signed transaction to the Bank.

1.  **Setup**:
    *   User A generates an RSA Key Pair.
    *   User A requests a certificate from the CA.
    *   CA issues a signed Certificate to User A.

2.  **Signing**:
    *   User A creates a transaction (e.g., "Pay $100").
    *   User A signs the transaction data with their **Private Key**.

3.  **Transmission**:
    *   User A sends: `[Transaction Data] + [Signature] + [Certificate]`.

4.  **Verification (at the Bank)**:
    *   **Step 1: Validate Trust**: The Bank checks User A's **Certificate**. It verifies the certificate's signature using the **CA's Public Key**.
        *   *Result*: "This certificate is valid and was issued by our CA. The Public Key inside belongs to User A."
    *   **Step 2: Validate Data**: The Bank extracts User A's **Public Key** from the valid certificate.
    *   **Step 3: Verify Signature**: The Bank uses User A's Public Key to verify the signature on the `[Transaction Data]`.
        *   *Result*: "The transaction was definitely signed by User A and has not been modified."
