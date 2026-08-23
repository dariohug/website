import pwn
from time import sleep
from lab_utils import login, print_buf
from Crypto.PublicKey import RSA
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_OAEP
import base64

def verify_signature(message, signature, key_pem):
    pub_key = RSA.import_key(key_pem)
    h = SHA256.new(message)
    try:
        pkcs1_15.new(pub_key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False
    
def encrypt_RSA_to_b64(message,key):
        cipher_rsa = PKCS1_OAEP.new(key)
        ct = cipher_rsa.encrypt(message.encode('utf-8'))
        ct_b64 = base64.b64encode(ct).decode('utf-8')  
        return ct_b64

con, buf = login(5)

# RSA with PKCS1_OAEP

lines = buf.decode(errors="replace").split("\n")

for i, line in enumerate(lines): 
    line = line.strip()
    if "Bank public key (PEM, base64):" in line:
        public_key_b64 = lines[i+1]
    if "Your password is: " in line:
        password = line.split(" ")[-1]

con.sendline(b"continue") 

buf = con.recvrepeat(timeout=1)
# print(f"\n{buf.decode(errors='replace')}\n")

public_key_b = base64.b64decode(public_key_b64)
password_b = bytes(password, 'utf-8')

lines = buf.decode(errors="replace").split("\n")

for i, line in enumerate(lines): 
    line = line.strip()
    if "Message from" in line:
        IP = line.split(" ")[2]
    if "Signature (base64): " in line:
        signature = line.split(" ")[-1]
        signature_b = base64.b64decode(signature)
        if verify_signature(password_b, signature_b, public_key_b): 
            break 

print(IP) 
con.sendline(IP.strip(":"))

print_buf(con)
sleep(3)

ciphertext = encrypt_RSA_to_b64(password, RSA.import_key(public_key_b)) 

print(ciphertext)
con.sendline(ciphertext) 

buf = con.recvrepeat(timeout=3)
print(f"\n{buf.decode(errors='replace')}\n")    


