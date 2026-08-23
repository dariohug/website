import pwn
from time import sleep
from lab_utils import login, print_buf
import hashlib 


con, buf = login(1)

for round in range(1, 6): 

    # print(f"round: {round}")

    lines = buf.decode(errors="replace").split("\n")

    prime = None

    for i, line in enumerate(lines): 
        line = line.strip()
        if f"Round {round}:" in line:
            prime = lines[i+2].split(" ")[-1]
            break 

    prime_int = int(prime, 16)
    p_minus_1 = prime_int - 1

    # factor p-1
    x = p_minus_1
    prime_factors = []
    i = 2
    while i * i <= x:
        if x % i == 0:
            prime_factors.append(i)
            while x % i == 0:
                x //= i
        i += 1
    if x > 1:
        prime_factors.append(x)

    # find generator
    for g in range(2, prime_int):
        if all(pow(g, p_minus_1 // q, prime_int) != 1 for q in prime_factors):
            generator = g
            break

    print(f"found a generator: {generator}")

    generator = hex(generator)

    con.sendline(generator)

    buf = con.recvrepeat(timeout=1)
    print(buf)


print_buf(con)
