import pwn
from time import sleep
from lab_utils import login, print_buf


con, buf = login(6)

lines = buf.decode(errors="replace").split("\n")

for line in lines:
    if "p1:" in line.lower():
        plain_text_1 = line.split()[-1]
    if "c1:" in line.lower(): 
        cipher_text_1 = line.split()[-1]
    if "c2:" in line.lower(): 
        cipher_text_2 = line.split()[-1]

print(f"Plain Text 1: {plain_text_1}")
print(f"Cipher Text 1: {cipher_text_1}")
print(f"Cipher Text 2: {cipher_text_2}")

# key = P XOR C

pt1 = plain_text_1.encode()
ct1 = bytes.fromhex(cipher_text_1)
ct2 = bytes.fromhex(cipher_text_2)

key_bytes = bytes(a ^ b for a, b in zip(pt1, ct1))

key = key_bytes.hex()

print(f"key : {key}")

plaint_text_2_bytes = bytes(a ^ b for a, b in zip(ct2, key_bytes))

plain_text_2 = plaint_text_2_bytes.decode(errors="replace")

print(f"plain text 2 : {plain_text_2}")

con.sendline(plain_text_2)

print_buf(con)