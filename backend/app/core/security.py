# 加密模块

import base64
import hashlib
from cryptography.fernet import Fernet

# 格式化加密秘钥，由于用户输入的秘钥可能长度不符合要求，我们需要对其进行处理
def format_key(key: str) -> bytes:
    # 使用 SHA-256 哈希算法将输入的秘钥转换为固定长度的字节串
    hash_key = hashlib.sha256(key.encode("utf-8")).digest()
    # 将哈希后的字节串进行 Base64 编码，得到符合 Fernet 要求的秘钥格式
    return base64.urlsafe_b64encode(hash_key)

# 加密函数，使用 Fernet 对数据进行加密
def encrypt(data: str, secret: str) -> str:
    # 格式化秘钥
    key = format_key(secret)
    # 创建 Fernet 加密器
    fernet = Fernet(key)
    # 加密数据并返回加密后的字符串
    return fernet.encrypt(data.encode("utf-8")).decode("utf-8")

# 解密函数，使用 Fernet 对数据进行解密
def decrypt(token: str, secret: str) -> str:
    # 格式化秘钥
    key = format_key(secret)
    # 创建 Fernet 加密器
    fernet = Fernet(key)
    # 解密数据并返回解密后的字符串
    return fernet.decrypt(token.encode("utf-8")).decode("utf-8")