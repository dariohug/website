#!/usr/bin/env python3
import pwn
import time
from lab_utils import login, print_buf
import hashlib
import hmac
import re
from Crypto.Cipher import AES
import binascii
from Crypto.Hash import SHA3_256
import string

alphabet = list(string.ascii_uppercase + string.digits)

def h(mb):
    h = SHA3_256.new(mb)
    return h.hexdigest()


def checkpwd(pwd, pwdhash):
    if len(pwd) < len(pwdhash):
        return False
    for i in range(len(pwd)):
       if i >= len(pwdhash):
           return False
       current_hash = h(pwd[i].encode())

       if current_hash != pwdhash[i]:
           return False
    return True


con, buf = login(6)

lines = buf.decode(errors="replace").split("\n")

hash_LUT = {}
password = []

for i, line in enumerate(lines): 
    if "each character:" in line: 
        for j in range(10):
            password.append(lines[i+j+2].strip("\t"))

# print(hash_dict)

for letter in alphabet: 
    hash_LUT[h(bytes(letter, 'utf-8'))] = letter

solved_pw = ""

for i in password:
    for j in hash_LUT.keys(): 
        if i == j: 
            solved_pw += hash_LUT[j]
            break

print(solved_pw)

con.sendline(solved_pw) 

print_buf(con)