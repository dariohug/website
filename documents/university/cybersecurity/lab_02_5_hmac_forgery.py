#!/usr/bin/env python3
import pwn
import time
from lab_utils import login, print_buf
import hashlib
import hmac
import re
from Crypto.Cipher import AES
import binascii

con, buf = login(5)


lines = buf.decode(errors="replace").split("\n")

key_hex = None

text = "\n".join(lines)
m = re.search(r'Use key=\s*([0-9a-fA-F]+)', text)
if m:
    key_hex = m.group(1)

# print(key_hex)
message = b"Username:Alice"

hmac_sha = hmac.new(bytes.fromhex(key_hex), message, hashlib.sha256).hexdigest()

con.sendline(hmac_sha) 
buf = con.recvrepeat(timeout=1)


print_buf(con)

lines = buf.decode(errors="replace").split("\n")

iv_hex = None


print(f"new buffer: {buf}")

text = buf.decode(errors="replace")
# find lines that mention "IV" and capture the first 32-hex token after it
m = re.search(r'IV of\s*([^\s]+)', text, re.IGNORECASE)
iv_hex = m.group(1).lower()

print(f"Iv: {iv_hex}\n")

plaintext = b"Username:Alice"

# convert hex -> bytes
key = bytes.fromhex(key_hex)
nonce = bytes.fromhex(iv_hex)

cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
ciphertext, tag = cipher.encrypt_and_digest(plaintext)

ct_hex  = ciphertext.hex()
tag_hex = tag.hex()
combined_hex = (ciphertext + tag).hex()

print("ciphertext (hex):", ct_hex)
print("tag        (hex):", tag_hex)
print("ciphertext||tag (hex):", combined_hex)

con.sendline(ct_hex)

print_buf(con) 

con.sendline(tag_hex)

print_buf(con)
