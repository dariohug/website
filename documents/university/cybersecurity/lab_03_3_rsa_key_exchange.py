import pwn
from time import sleep
from lab_utils import login, print_buf
import base64 
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import unpad

con, buf = login(3)

key = RSA.generate(2048)
public_key = key.publickey().export_key('PEM')
private_key = key.export_key('PEM')
base64_public_key = base64.b64encode(public_key).decode('utf-8') # Send this over the network

con.sendline(base64_public_key) 

buf = con.recvrepeat(timeout=1)
print(f"\n{buf.decode(errors='replace')}\n")

lines = buf.decode(errors="replace").split("\n")

for i, line in enumerate(lines): 
    line = line.strip()
    if "a key encrypted using your RSA public key" in line:
        enc_key_b64 = line.split(" ")[-1]
    if "(In base64) IV:" in line:
        IV_b64 = line.split(" ")[-1]
    if "(In base64) Encrypted flag:" in line:
        enc_flag_b64 = line.split(" ")[-1]
    
print(f"IV: {IV_b64}\nFlag: {enc_flag_b64}")

ciphertext = base64.b64decode(enc_flag_b64)
iv = base64.b64decode(IV_b64)

rsa_key = RSA.import_key(private_key)
enc_key_bytes = base64.b64decode(enc_key_b64)

cipher_rsa = PKCS1_OAEP.new(rsa_key)
aes_key = cipher_rsa.decrypt(enc_key_bytes)  # should be 16 bytes for AES-128

cipher = AES.new(aes_key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

print("Decrypted flag:", plaintext.decode('utf-8'))