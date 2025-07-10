from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64
import os

def encrypt_token(token: str, key: bytes) -> str:
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct_bytes = cipher.encrypt(pad(token.encode('utf-8'), AES.block_size))
    result = base64.b64encode(iv + ct_bytes).decode('utf-8')
    return result

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # 讀取環境變數中的 key
    key = bytes.fromhex(os.getenv("key"))
    
    token = "MTM5Mjc0NTI2NzY0ODAwODM3Ng.GyFy3T.FATkfJYxNGl2AF_npbY5ll4IlcjjiSJWI27XM0"
    print("原始 token:", token)

    encrypted = encrypt_token(token, key)
    print("加密後 (base64):", encrypted)
