import pwn
import time
from lab_utils import login, print_buf
import hashlib 

con, buf = login(3)

# 10 Hex is 40 bits

CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"

def sHashPlus(msg): 
    return hashlib.md5(msg.encode()).hexdigest()[:10]

def to_base36(n):
    if n == 0:
        return "0"
    out = []
    while n > 0:
        out.append(CHARS[n % 36])
        n //= 36
    return "".join(reversed(out))

seen = {}
start = time.time()
limit = 2**20 
for i in range(limit):
    uname = to_base36(i)
    h = sHashPlus(uname)
    if h in seen:
        other = seen[h]  
        if other != uname:
            print("FOUND candidate collision")

            # Verify both usernames produce the same truncated hash:
            print(f"sHashPlus({other!r}) = {sHashPlus(other)}")
            print(f"sHashPlus({uname!r})  = {sHashPlus(uname)}")
            break

    else:
        seen[h] = uname
    # optional progress output
    if (i+1) % 10000 == 0:
        elapsed = time.time() - start
        print(f"    tried {i+1} candidates... elapsed {elapsed:.2f}s, memory map size {len(seen)}")

con.sendline(uname)
time.sleep(1)
con.sendline(other) 

print_buf(con)