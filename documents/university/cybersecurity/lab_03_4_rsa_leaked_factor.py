import pwn
from time import sleep
from lab_utils import login, print_buf
import base64 
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import unpad
from Crypto.Util.number import inverse

# PKCS1_OAEP

con, buf = login(4)

lines = buf.decode(errors="replace").split("\n")

for i, line in enumerate(lines): 
    line = line.strip()
    if "Alice announces her public key (in PEM format encoded as base64) as follows:" in line:
        public_key_b64 = lines[i+1]
    if "Intercepted message (in base64):" in line:
        ciphertext_b64 = lines[i+1]
    if "Hint: you have discovered one RSA factor (in hex)" in line:
        rsa_factor_hex = line.split(" ")[-1]


# Decode fields
public_key_b = base64.b64decode(public_key_b64)
ciphertext_b = base64.b64decode(ciphertext_b64)
p = int(rsa_factor_hex, 16)

print(f"Public Key: {public_key_b}\n Ciphertext: {ciphertext_b} \n RSA Factor: {p}")

public_key = RSA.importKey(public_key_b)
n = public_key.n
e = public_key.e

# n = p * q -> p,q elmt(primes)
q = n // p

# phi(n) = (p-1)*(q-1) 
phi = (p - 1) * (q - 1)

# d equiv e^(-1) mod phi(n) 
d = inverse(e, phi)

# Construct the private key object
priv_key = RSA.construct((n, e, d, p, q))

# Decrypt the message
cipher = PKCS1_OAEP.new(priv_key)
plaintext = cipher.decrypt(ciphertext_b)

print(plaintext.decode())