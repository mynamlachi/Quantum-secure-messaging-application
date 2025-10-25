# Quantum Secure Messaging Application 🔒

A **Quantum Computing Simulator** that demonstrates the **BB84 Quantum Key Distribution (QKD)** protocol for secure communication.  
This project shows how Alice and Bob can share a cryptographic key securely using quantum principles — and how eavesdropping (Eve) can be detected.

---

## 🚀 Features

- Simulates **BB84 Quantum Key Distribution**
- Detects **eavesdropping attacks (Eve)** via error rates
- Uses shared quantum key to **encrypt and decrypt messages**
- Simple **CLI interface**
- 100% **Python-based** (no quantum hardware required)

---

## 🧩 How It Works

1. **Alice** generates random bits and bases (quantum states).  
2. **Bob** measures with random bases.  
3. Both reveal their bases and keep bits measured with matching bases.  
4. A small subset of bits is used to estimate **error rate**.  
5. If the error rate is below threshold → key is accepted.  
6. Shared key is used for **message encryption/decryption** via XOR.

---

## 🧠 Requirements

- Python 3.7 or higher  
- No external dependencies

---

## 🖥️ Usage

### 1️⃣ Generate a Quantum Key
```bash
python Quantum_Secure_Messaging_App.py --generate-key --length 256
```
This simulates a BB84 run and outputs a shared secret key in hexadecimal format.

### 2️⃣ Send (Encrypt/Decrypt) a Message
```bash
python Quantum_Secure_Messaging_App.py --send "Hello Quantum World!" --length 128
```
Encrypts and decrypts a message using the generated quantum key.

### 3️⃣ Simulate Eavesdropping (Eve)
```bash
python Quantum_Secure_Messaging_App.py --send "Top Secret" --length 128 --eve --verbose
```
You’ll notice an **increased error rate**, showing that Eve’s presence disrupts quantum communication.

---

## 📊 Example Output

```
--- Quantum Secure Messaging Demo ---
Requested key length (bits): 256
Estimated error rate from sample: 0.0312
Shared key (hex, first 64 chars): 5f7d4b9e13ab7c2e...
Original message: Hello Quantum World!
Cipher (hex): 1a7b2c4d3e9f...
Decrypted message: Hello Quantum World!
```

---

## 🧰 Project Structure

```
Quantum_Secure_Messaging_App.py   # Main simulator file
README.md                         # Documentation file
```



---

## 📚 License

This project is open-source under the **MIT License**.

---


