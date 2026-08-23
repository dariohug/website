import pwn
from time import sleep
from lab_utils import login, print_buf
from Crypto.PublicKey import RSA
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_OAEP
import re
import json

# HMAC-SHA256(k, R1)

con, buf = login(6)

#Idea: Send hex value to computer and see how its MAC'ed 
# Compute key, send requested nonce back at computer 

nonce = hex(100)[2:]
m = {'message': 'This is Bob. MAC this nonce to prove that you are Bobs computer', 'nonce' : nonce}

con.sendline(json.dumps(m).encode()) 

buf = con.recvrepeat(timeout=1)
print(f"\n{buf.decode(errors='replace')}\n")

lines = buf.decode(errors="replace").split("\n")

for i, line in enumerate(lines):
    if "Likewise, if you are Bob" in line: 
        line = line.split(":")
        nonce_comp = (line[2].strip(" ").strip('"')).split(" ")[0].strip('", ')
        token = line[3].strip(" ").strip("}").strip('"')

print(f"Nonce: {nonce_comp}\nToken: {token}") 

### different con
con1, buf1 = login(6)

nonce = nonce_comp
m = {'message': 'This is Bob. MAC this nonce to prove that you are Bobs computer', 'nonce' : nonce}

con1.sendline(json.dumps(m).encode()) 
buf1 = con1.recvrepeat(timeout=1)
print(f"\n{buf1.decode(errors='replace')}\n")
lines = buf1.decode(errors="replace")


json_objects_str = re.findall(r'\{.*?\}', lines, re.DOTALL)

parsed_messages = []

for json_str in json_objects_str:
    try:
        data_dict = json.loads(json_str)
        parsed_messages.append(data_dict)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON string: {json_str[:50]}... Error: {e}")

print(f"responce: {data_dict['token']}")

###
response_msg = {'token': data_dict['token']}
con.sendline(json.dumps(response_msg).encode())

buf = con.recvrepeat(timeout=1)
print(f"\n{buf.decode(errors='replace')}\n")




