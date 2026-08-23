import pwn
from time import sleep
from lab_utils import login, print_buf


con, buf = login(3)

lines = buf.decode(errors="replace").split("\n")

for line in lines:
    if "C:" in line:
        ciphertext = line.split()[-1]
    if "The plaintext contains a character sequence:" in line: 
        sequence = line.split()[-1]

print(f"ciphertext = {ciphertext}")
print(f"Sequence = {sequence}")

# Shift cipher: Enc(x) = x+k mod 26 
# Key is unknown here...

solution = None
k = 0

while(not solution): 
    plaintext = ""
    for ch in ciphertext:
        if ch.islower():
            plaintext += chr((ord(ch) - ord('a') - k) % 26 + ord('a'))
        else :
            plaintext += chr((ord(ch) - ord('A') - k) % 26 + ord('A'))
        
    if sequence in plaintext:
        print(f"HIT! Key = {k}")
        solution = plaintext
    else:
        print(f"NO HIT... k = {k}")
    k += 1

con.sendline(solution) 

print_buf(con) 
