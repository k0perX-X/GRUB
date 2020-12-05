from Crypto.Cipher import DES
from output.encrypt_keys import encrypt_keys
from random import randint


def pad(text):
    while len(text) % 256 != 0:
        x = randint(0, 2)
        if x == 0:
            text += b'|'
        elif x == 1:
            text += b'\\'
        elif x == 2:
            text += b'/'
    return text


def unpad(text):
    j = len(text)
    for i in text[::-1]:
        if i != 124 and i != 92 and i != 47:
            break
        else:
            j -= 1
    return text[:j]


def encrypt(num_key, s):
    des = DES.new(encrypt_keys[num_key], DES.MODE_ECB)
    return des.encrypt(pad(s))


def decrypt(num_key, s):
    des = DES.new(encrypt_keys[num_key], DES.MODE_ECB)
    return unpad(des.decrypt(s))
