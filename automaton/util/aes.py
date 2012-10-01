import os
import settings
import base64
from Crypto.Cipher import AES
import hashlib

MODE = AES.MODE_ECB

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
    CIPHER = AES.new(key, MODE)
    res = CIPHER.encrypt(st)
    return base64.urlsafe_b64encode(res)

def decrypt(st, key):
    enc = base64.urlsafe_b64decode(st)
    CIPHER = AES.new(key, MODE)
    res = CIPHER.decrypt(enc)
    return res.rstrip(settings.PAD).rstrip(settings.INTERRUPT)

def generate_key():
    return os.urandom(16)
