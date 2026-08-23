import pwn
from time import sleep
from lab_utils import login, print_buf


con, buf = login(4)

lines = buf.decode(errors="replace").split("\n")

for line in lines:
    if "(in hexstr) ciphertext:" in line.lower():
        ciphertext = line.split()[-1]
    if "(in hexstr) key:" in line.lower(): 
        key = line.split()[-1]

print(f"ciphertext: {ciphertext}")
print(f"key: {key}")

# OTP: 
# Ciphertext = P XOR K 
# Plaintext = C XOR K 

ct = bytes.fromhex(ciphertext)
kb = bytes.fromhex(key)

# XOR byte-by-byte
plain_bytes = bytes(a ^ b for a, b in zip(ct, kb))

plain_text = plain_bytes.decode(errors="replace")

print(plain_text)

con.sendline(plain_text)

print_buf(con)