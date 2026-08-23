import pwn
import time
from lab_utils import login, print_buf
import hashlib 


con, buf = login(2)

lines = buf.decode(errors="replace").split("\n")

target_hash = None

for k, line in enumerate(lines):
    line = line.strip()
    if "sHash(mypassword))." in line:
        target_hash = lines[k+1]

if not target_hash:
    print("target not foound!")


def brute_force_preimage(target):
    """
    Brute force an input whose md5(message).hexdigest()[:5] == target..
    """
    target = target.lower()
    start = time.time()
    limit = 1 << 20  # 2^20
    for i in range(limit):
        candidate = str(i)
        h = hashlib.md5(candidate.encode()).hexdigest()[:5]
        if h == target:
            elapsed = time.time() - start
            print(f"FOUND CANDIDAT: {candidate}  (tries={i+1}, elapsed={elapsed:.2f}s)")
            return candidate
        if (i & 0x3FFFF) == 0x3FFFF:  # every 262,144 tries
            print(f"    tried {i+1}/{limit} candidates... elapsed {time.time()-start:.2f}s")
    print("NO CANDIDATE FOUND")
    return None

candidate = brute_force_preimage(target_hash)

con.sendline(candidate)

print_buf(con)