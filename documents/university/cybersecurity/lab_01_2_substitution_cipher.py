import pwn
from time import sleep
from lab_utils import login


con, buf = login(2)

plain_alphabet = buf.decode(errors="replace").split("\n")[2].split()[0]
print(f"plain: {plain_alphabet}")
cipher_alphabet = buf.decode(errors="replace").split("\n")[5].split()[0]
print(f"cipher: {cipher_alphabet}")


lines = buf.decode(errors="replace").split("\n")

plain_text = None
for line in lines:
    if "Encrypt the following plaintext:" in line:
        plain_text = line.split()[-1]
        break

dict = {}

for p, c in zip(plain_alphabet, cipher_alphabet):
    dict[p] = c

print(dict)

cipher_text = ""
for ch in plain_text:
    cipher_text += dict[ch]

# print(cipher_text)

con.sendline(cipher_text)

buf = con.recvrepeat(timeout=1)

print(f"\n{buf.decode(errors='replace')}\n")
lines = buf.decode(errors="replace").split("\n")


cipher_text = None
for line in lines:
    if "Decrypt the following ciphertext:" in line:
        cipher_text = line.split()[-1]
        break
   
print(f"cipher text new = {cipher_text}")

inv_dict = {v: k for k, v in dict.items()}

plain_text = ""
for ch in cipher_text:
    plain_text += inv_dict[ch]

print(f"plain text new: {plain_text}")

con.sendline(plain_text)

buf = con.recvrepeat(timeout=1)

print(f"\n{buf.decode(errors='replace')}\n")
