import pwn
from time import sleep
from lab_utils import login, print_buf
import hashlib 


con, buf = login(1)

lines = buf.decode(errors="replace").split("\n")

hash_pairs = {}

for line in lines:
    line = line.strip()
    if "UUID:" in line:
        index = line.split(" ")[0]
        uuid_value = line.split("UUID:")[1].strip()
        hash_pairs[index] = {"UUID": uuid_value}
    elif "Hash(UUID):" in line:
        index = line.split(" ")[0]
        hash_value = line.split("Hash(UUID):")[1].strip()
        if index in hash_pairs:
            hash_pairs[index]["Hash"] = hash_value

# for k, v in hash_pairs.items():
#     print(f"{k}: UUID={v['UUID']}, Hash={v['Hash']}")

result = ""

for key, pair in hash_pairs.items():
    uuid_bytes = pair["UUID"].encode()  
    computed_hash = hashlib.sha256(uuid_bytes).hexdigest()

    if computed_hash == pair["Hash"]:
        result += "Y"
    else:
        result += "N"

print(f"Reuslt = {result}, Len = {len(result)}")

con.sendline(result) 

print_buf(con)
