import re
import pwn
from lab_utils import login, print_buf
import os
from time import sleep

con, buf = login(8)

def recv_cipher_hex():
    """Read a line and extract the longest hex substring"""
    line = con.recvline(timeout=1)
    if not line:
        print("inproper return of oracle")
        return ""
    s = line.decode(errors='replace').strip()
    
    # find longest hex substring of even length (common ciphertext lengths are >= 32 chars)
    matches = re.findall(r'[0-9a-fA-F]+', s)
    if not matches:
        return ""
    # choose the longest match (most likely the ciphertext)
    hex_candidate = max(matches, key=len)
    # ensure even length (hex must be even number of chars)
    if len(hex_candidate) % 2 == 1:
        hex_candidate = hex_candidate[:-1]
    return hex_candidate.lower()

prefix = b'\x00' * 14
zeros14 = b'\x00' * 14

# 1) get target block C0
con.sendline(prefix.hex().encode())               # send empty input (newline)
resp_hex = recv_cipher_hex()
C0 = bytes.fromhex(resp_hex)[0:16]
print(f"Answer for empty block C0: {C0.hex()}, Len: {len(C0)}")

secret = None

# 2) brute-force all 2-byte secrets
for x in range(2**16):

    s = x.to_bytes(2, 'big')
    payload = prefix + s + zeros14
    con.sendline(payload.hex().encode())
    resp_hex = recv_cipher_hex()

    cipher_bytes = bytes.fromhex(resp_hex)

    if x % 1000 == 0:  
        print(f"Tried: {x}/{2**16}")
        print(f"Len Responce: {len(cipher_bytes)}, \nC0: {cipher_bytes[0:16].hex()}, \nC1: {cipher_bytes[16:32].hex()}")

    block1 = cipher_bytes[16:32]
    if block1 == C0:
        print("Found secret candidate:", x, hex(x))
        secret =  f"{x:04x}" 
        break
else:
    print("No candidate matched.")


if secret:
    con.sendline(b"c")
    sleep(0.5)
    con.sendline(secret.encode())
    print_buf(con)