import os
import settings
import base64
from Crypto.Cipher import AES
import hashlib
import random

MODE = AES.MODE_CBC

def pad(st):
    st = ''.join([st, settings.INTERRUPT])
    st_len = len(st)
    rem_len = settings.BLOCK_SIZE-st_len
    padding_len = rem_len%settings.BLOCK_SIZE
    padding = settings.PAD*padding_len
    final_st = ''.join([st, padding])
    return final_st

def encrypt(st, key):
    st = pad(st)
    IV = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    CIPHER = AES.new(key, MODE, IV)
    res = CIPHER.encrypt(st)
    res = IV+res
    return base64.urlsafe_b64encode(res)

def decrypt(st, key):
    enc = base64.urlsafe_b64decode(st)
    IV = enc[:16]
    CIPHER = AES.new(key, MODE, IV)
    res = CIPHER.decrypt(enc[16:])
    return res.rstrip(settings.PAD).rstrip(settings.INTERRUPT)

def generate_key():
    return os.urandom(32)
