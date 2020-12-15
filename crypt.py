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


def stringing(byte_string):
    s = ''
    for i in byte_string:
        s += chr(i)
    return s


def unstringing(s):
    byte_string = b''
    for i in s:
        byte_string += bytes([ord(i)])
    return byte_string


def encrypt(num_key, s):
    des = DES.new(encrypt_keys[num_key], DES.MODE_ECB)
    return stringing(des.encrypt(pad(s)))
    #return des.encrypt(pad(s))


def decrypt(num_key, s):
    des = DES.new(encrypt_keys[num_key], DES.MODE_ECB)
    return unpad(des.decrypt(unstringing(s)))
    #return unpad(des.decrypt(s))
