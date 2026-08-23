import pwn
from time import sleep
from lab_utils import login, print_buf
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA


con, buf = login(7)
"""
Protocol Overview

    1 User → Bank: Send challenge (Base64)
    2 Bank → User: Sign challenge using Bank's private key. Send signature result to User
    3 User → Bank: If signature is verified successfully, generate fresh symmetric key and encrypt it under the Bank's public key. Send the resulting ciphertext to the bank.
    4 Bank: Decrypts the symmetric key from (3.) and uses it to encrypt subsequent traffic using AES256-CBC.

HINTS:

    This protocol (asymmetric encrypt/decryption and signature) is implemented using Textbook RSA (i.e., without randomized padding or hashing).

    The bank uses the same key pair for encryption and signature operations.

    You have intercepted messages sent in steps 3 and 4.

    The step 4 message intercepted contains the encryption of the flag using AES256-CBC.

    Below is the python implementation of the function used to encrypt messages in step 4. (Note that the IV is prepended to the ciphertext.)"""

#Idea: sign_sk(enc_pk(k)) = k 

# AES encrypt function
def aes_encrypt(key, plaintext):
    """Encrypt plaintext using AES-256-CBC with random IV."""
    # Ensure key is 32 bytes (256 bits)
    if len(key) < 32:
        key = hashlib.sha256(key).digest()
    else:
        key = key[:32]
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ct = cipher.encrypt(pad(plaintext.encode('utf-8'), AES.block_size))
    return base64.b64encode( iv + ct).decode('utf-8')

lines = buf.decode(errors="replace").split("\n")

for i, line in enumerate(lines):
    if "Message 3 - Encrypted Symmetric Key:" in line: 
        encrypted_symmetric_key = lines[i+1]
    if "Message 4 - Encrypted Flag:" in line: 
        encrypted_flag = lines[i+1]

print(f"Encryped Key: {encrypted_symmetric_key}\nEncrypted Flag: {encrypted_flag}")

con.sendline(encrypted_symmetric_key) 

buf = con.recvrepeat(timeout=1)
print(f"\n{buf.decode(errors='replace')}\n")

lines = buf.decode(errors="replace").split("\n")

for i, line in enumerate(lines):
    if "Signature (base64):" in line: 
        decrypted_key = lines[i+1]

raw_key = base64.b64decode(decrypted_key)

aes_key = raw_key[-32:] 

decoded_flag = base64.b64decode(encrypted_flag)

iv = decoded_flag[:16]
ct = decoded_flag[16:]

cipher = AES.new(aes_key, AES.MODE_CBC, iv)
plaintext_padded = cipher.decrypt(ct)

flag = unpad(plaintext_padded, AES.block_size).decode('utf-8')

print(f"\n[FOUND FLAG]: {flag}")
