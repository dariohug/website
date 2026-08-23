import pwn
from time import sleep
from lab_utils import login, print_buf
import base64 
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

con, buf = login(2)

lines = buf.decode(errors="replace").split("\n")


for i, line in enumerate(lines): 
    line = line.strip()
    if "DHKE parameters (in hex):" in line:
        prime = lines[i+1].split(" ")[-1]
    if "Generator:" in line:
        generator = line.split(" ")[-1]
        break 

prime = int(prime, 16) 
generator = int(generator, 16) 

print(f"prime: {prime} \ngenerator: {generator}")

# Idea: Public Key = generator ** (secret key) mod prime 

private_key = 12

pubic_key = (generator ** private_key) % prime

print(pubic_key)

con.sendline(hex(pubic_key))

buf = con.recvrepeat(timeout=1)
lines = buf.decode(errors="replace").split("\n")
print(lines)

for i, line in enumerate(lines): 
    line = line.strip()
    if "My public key (in hex): " in line:
        public_key_b = lines[i].split(" ")[-1]
    if "nonce" in line:
        line = line.split(" ")
        for i, elmt in enumerate(line): 
            if "nonce" in elmt: 
                nonce = line[i+1].strip(',').strip('"')
            if "header" in elmt: 
                header = line[i+1].strip(',').strip('"')
            if "ciphertext" in elmt: 
                ciphertext = line[i+1].strip(',').strip('"')
            if "tag" in elmt: 
                tag = line[i+1].strip("}").strip(',').strip('"')
        break 

# print(f"Their Public Key: {public_key_b} \nnonce: {nonce} \nheader: {header} \nciphertext: {ciphertext} \ntag: {tag}")

# Session Key a = public_key_b ** private_key_a mod prime 

session_key_a = (int(public_key_b, 16) ** private_key) % prime
sess_key_bytes = session_key_a.to_bytes(session_key_a.bit_length(), byteorder='big')

aes_key = SHA256.new(sess_key_bytes).digest()

nonce_b = base64.b64decode(nonce)
header_b = base64.b64decode(header)
cipher_b = base64.b64decode(ciphertext)
tag_b = base64.b64decode(tag)

cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce_b)
cipher.update(header_b)  # associated data
plaintext = cipher.decrypt_and_verify(cipher_b, tag_b)
print("Decrypted plaintext:", plaintext.decode())

