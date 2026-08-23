#!/usr/bin/env python3
import pwn
import time
import sys
from lab_utils import login, print_buf
import hashlib
from Crypto.Cipher import AES
import binascii
import re

def bytes_xor(var, key):
    return bytes(a ^ b for a, b in zip(var, key))

def hash_block(m, prevH):
    if len(m) > AES.block_size:
        raise ValueError('Block size must be 16 bytes')
    cipher = AES.new(m, AES.MODE_ECB)
    # AES.encrypt accepts any multiple of 16-bytes; prevH may be 32 bytes as in challenge
    enc = cipher.encrypt(prevH)
    return bytes_xor(enc, prevH)

con, buf = login(4)
banner = buf.decode(errors="replace")

token_match = re.search(r'`LAUGH` command with this token:\s*([0-9a-fA-F]{32,128})', banner)
if token_match:
    LAUGH_token_hex = token_match.group(1)
else:
    # fallback: find any long hex sequence in the banner
    m2 = re.search(r'\b([0-9a-fA-F]{32,128})\b', banner)
    LAUGH_token_hex = m2.group(1) if m2 else None

if not LAUGH_token_hex:
    print("[!] Failed to extract LAUGH token from banner. Aborting.")
    con.interactive()
    sys.exit(1)

print("[+] Extracted LAUGH token (hex):", LAUGH_token_hex)
# sanity check length
if len(LAUGH_token_hex) % 2 != 0:
    print("[!] Token hex length is odd; invalid. Aborting.")
    con.interactive()
    sys.exit(1)

try:
    prevH = binascii.unhexlify(LAUGH_token_hex)
except Exception as e:
    print("[!] Failed to unhexlify token:", e)
    con.interactive()
    sys.exit(1)

print(f"[+] Token decoded: {len(prevH)} bytes")


remainder = b" FLAG"
# server pads with spaces to next 16-byte boundary
m2 = remainder.ljust(16, b' ')
assert len(m2) == 16

print("[+] Next block (m2) bytes (len=16):", m2)

newH = hash_block(m2, prevH)
forged_hex = binascii.hexlify(newH).decode()
print("[+] Forged MAC (hex):", forged_hex)
print("[+] Forged MAC length (hex chars):", len(forged_hex))

cmd = "LAUGH FLAG"
print("[+] Sending command:", cmd)
con.sendline(cmd)
time.sleep(0.1)
print("[+] Sending forged token")
con.sendline(forged_hex)

print_buf(con)
