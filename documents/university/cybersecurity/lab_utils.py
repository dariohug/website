import pwn
from time import sleep

def login(challenge):
    connection = pwn.remote("spyridon.ifi.uzh.ch", 26052)

    connection.recvuntil(b"Enter your Spyridon username:", timeout=60)

    # send our username followed by a newline (like `echo user | nc ...`)
    # sleep(0.5)

    connection.sendline(b"dhug")
    # print("sent username")

    connection.recvuntil(b"Enter 1-7:", timeout=60)

    connection.sendline(str(challenge)) 

    # print("sent challenge")

    buf = connection.recvrepeat(timeout=3)

    print(f"\n{buf.decode(errors='replace')}\n")

    sleep(1)
    return connection, buf

def print_buf(con): 
    buf = con.recvrepeat(timeout=1)
    print(f"\n{buf.decode(errors='replace')}\n")

