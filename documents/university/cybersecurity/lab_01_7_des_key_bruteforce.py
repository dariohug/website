from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import DES
import random
import pwn
from time import sleep
from lab_utils import login, print_buf
import numpy as np


def generate_key_from_int(x):
    """
    Generates a padded DES key from the supplied interger. 
      For our purposes x is a 6 digit number and the DES key size is 64 bits (8 bytes)
    :param: x (int) - The integer to be converted into a key
    :return: The padded DES key in bytes
    """
    key_bytestr = str(x).encode()
    return pad(key_bytestr, DES.block_size)

def single_encrypt(m, key):
    m = str.encode(m)
    msg = pad(m,DES.block_size)
    cipher1 = DES.new(key, DES.MODE_ECB)
    return  cipher1.encrypt(msg)

def single_decrypt(ciphertext, key):
    cipher = DES.new(key, DES.MODE_ECB)
    return cipher.decrypt(ciphertext)

def double_decrypt(ciphertext, first_key, second_key):
    """
    Completely decrypts the 2DES ciphertext using the two keys provided
    :param: ciphertext (bytes) - The 2DES ciphertext to decrypt
    :param: first_key (bytes) - The decryption key for the first decryption
    :param: second_key (bytes) - The decryption key for the second decryption
    :return: The plaintext flag (bytes)
    """
    cipher = DES.new(first_key, DES.MODE_ECB)
    temp = cipher.decrypt(ciphertext)

    cipher2 = DES.new(second_key, DES.MODE_ECB)
    plaintext = cipher2.decrypt(temp)

    plaintext = unpad(plaintext, DES.block_size)
    return plaintext

con, buf = login(7)

lines = buf.decode(errors="replace").split("\n")

plain_text_2 = "Good luck!"

for i, line in enumerate(lines):
    if "Here is the flag (in hex) encrypted using 2DES." in line:
        cipher_text_1 = lines[i+1].split()[-1]
    if "and the same keys" in line.lower(): 
        cipher_text_2 = lines[i+1].split()[-1]

print(f"Cipher Text 1: {cipher_text_1}")
print(f"Cipher Text 2: {cipher_text_2}")
print(f"Plain Text 2: {plain_text_2}")

# Breaking 2DES: 
# 

ciphertext_bytes = bytes.fromhex(cipher_text_1)

padded_plain_text_2 = pad(str.encode(plain_text_2), DES.block_size) 

key_space_table = {}

# Fill the table with possible intermediate results 
for k1_int in range(10**6):
    k1 = generate_key_from_int(k1_int) 
    intermediate = single_encrypt(plain_text_2, k1)
    key_space_table[intermediate] = k1_int

    if k1_int % 100000 == 0: 
        print(f"K1 tried: {k1_int}/{10**6}")

# The table is now full with Intermediate results coming from the encryption side
# print(f"Example from first side: {list(key_space_table.items())[0]}")

k1 = None
k2_int = None
# Look for a "meet-up" in the middle
for k2_int in range(10**6):
    k2 = generate_key_from_int(k2_int)
    intermediate = single_decrypt(bytes.fromhex(cipher_text_2), k2)

    # We check for every result from the decryption side if it is already in the table

    if intermediate in key_space_table:
        k1_int = key_space_table[intermediate]
        k1 = generate_key_from_int(k1_int)

        print(f"HIT!! Key1 is :{k1.decode()}, Key2 is :{k2.decode()}")
        break
    if k2_int % 100000 == 0:    
        print(f"K2 tried: {k2_int}/{10**6}")

# print(f"Example from second side: {intermediate}")

if (not k1):
    print("No Key pair Found ")
else:
    plain_text_1 = double_decrypt(bytes.fromhex(cipher_text_1), k2, k1)
    print(f"Plain Text: {plain_text_1.decode()}")