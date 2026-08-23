import pwn
from time import sleep
from lab_utils import login

connection, buf = login(1)

ciphertext = buf.decode(errors="replace").split("\n")[1].split()[1]
key = int(buf.decode(errors="replace").split("\n")[2].split()[1])

plaintext = ""

for ch in ciphertext:
    if ch.islower():
        plaintext += chr((ord(ch) - ord('a') - key) % 26 + ord('a'))
    else :
        plaintext += chr((ord(ch) - ord('A') - key) % 26 + ord('A'))


print(f"solution = {plaintext} \n")

connection.sendline(plaintext)

# Part II 

buf = connection.recvrepeat(timeout=1)

print(f"\n{buf.decode(errors='replace')}\n")

plaintext = buf.decode(errors="replace").split("\n")[1].split()[1]
key = int(buf.decode(errors="replace").split("\n")[2].split()[1])

ciphertext = ""

for ch in plaintext: 
    if ch.islower():
        ciphertext += chr((ord(ch) - ord('a') + key) % 26 + ord('a'))
    elif ch.isupper():
        ciphertext += chr((ord(ch) - ord('A') + key) % 26 + ord('A'))
    else:
        ciphertext += ch 

connection.sendline(ciphertext)

buf = connection.recvrepeat(timeout=1)
print(f"\n{buf.decode(errors='replace')}\n")




