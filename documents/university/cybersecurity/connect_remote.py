#!/usr/bin/env python3
from pwn import remote, context
import re, sys

# Log level: "info" for concise output, use "debug" to see raw socket traffic
context.log_level = "debug"

# target host/port (update if needed)
HOST, PORT = "spyridon.ifi.uzh.ch", 26051

# regex to match flag pattern like: uzh{...}
FLAG_RE = re.compile(rb"uzh\{[^}]+\}")

def extract_flag(buf):
    """
    Search `buf` (bytes) for the first occurrence of uzh{...}.
    Return the matched string decoded to str, or "Flag not found".
    """
    m = FLAG_RE.search(buf)
    return m.group(0).decode() if m else "Flag not found"

def main():
    # open a TCP connection to the challenge server (raises on failure)
    r = remote(HOST, PORT, timeout=5)

    try:
        # wait (block) until the server prompts for username or timeout occurs
        # noticed that my connection is quite slow, therefore timeout of 60s
        r.recvuntil(b"Enter your username: ", timeout=60)

        # send our username followed by a newline (like `echo user | nc ...`)
        r.sendline(b"dhug")

        # collect whatever the server sends in short windows:
        # recvrepeat gathers all available data for `timeout` seconds.
        buf = r.recvrepeat(timeout=10)

        # extract and print the flag (or a "not found" message)
        print(extract_flag(buf))

    except (TimeoutError, EOFError) as e:
        # TimeoutError: no data in timeout window
        # EOFError: remote closed the connection
        print("error:", e, file=sys.stderr)

    finally:
        # ensure the connection is always closed
        r.close()

if __name__ == "__main__":
    main()
