import os
from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

load_dotenv()

def decrypt_token(encrypted_token: str, key: bytes) -> str:
    raw = base64.b64decode(encrypted_token)
    iv = raw[:16]
    ct = raw[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')

def get_token():
    key = bytes.fromhex(os.getenv("key"))
    encrypted_token = os.getenv("token")
    return decrypt_token(encrypted_token, key)
