#!/usr/bin/env python3
"""
RAGForge 密码加密工具
使用RSA公钥加密密码，与前端保持一致
"""

import base64
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Protocol.KDF import PBKDF2


def encrypt_password(password: str) -> str:
    """
    使用RSA公钥加密密码，与后端/前端一致
    """
    public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArq9XTUSeYr2+N1h3Afl/
z8Dse/2yD0ZGrKwx+EEEcdsBLca9Ynmx3nIB5obmLlSfmskLpBo0UACBmB5rEjBp
2Q2f3AG3Hjd4B+gNCG6BDaawuDlgANIhGnaTLrIqWrrcm4EMzJOnAOI1fgzJRsOO
UEfaS318Eq9OVO3apEyCCt0lOQK6PuksduOjVxtltDav+guVAA068NrPYmRNabVK
RNLJpL8w4D44sfth5RvZ3q9t+6RTArpEtc5sh5ChzvqPOzKGMXW83C95TxmXqpbK
6olN4RevSfVjEAgCydH6HN6OhtOQEcnrU97r9H0iZOWwbw3pVrZiUkuRD1R56Wzs
2wIDAQAB
-----END PUBLIC KEY-----"""
    rsa_key = RSA.importKey(public_key)
    cipher = Cipher_pkcs1_v1_5.new(rsa_key)
    password_base64 = base64.b64encode(password.encode('utf-8')).decode('utf-8')
    encrypted_password = cipher.encrypt(password_base64.encode())
    return base64.b64encode(encrypted_password).decode('utf-8')


def encrypt_password_plain(password: str) -> str:
    """
    明文密码加密（用于测试）
    """
    return password

def encrypt_password_base64(password: str) -> str:
    """
    Base64编码密码（用于测试）
    """
    return base64.b64encode(password.encode()).decode()

def encrypt_password_sha256(password: str) -> str:
    """
    SHA256哈希密码（用于测试）
    """
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def encrypt_password_direct_rsa(password: str) -> str:
    """
    直接RSA加密（不先Base64）
    """
    public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArq9XTUSeYr2+N1h3Afl/
z8Dse/2yD0ZGrKwx+EEEcdsBLca9Ynmx3nIB5obmLlSfmskLpBo0UACBmB5rEjBp
2Q2f3AG3Hjd4B+gNCG6BDaawuDlgANIhGnaTLrIqWrrcm4EMzJOnAOI1fgzJRsOO
UEfaS318Eq9OVO3apEyCCt0lOQK6PuksduOjVxtltDav+guVAA068NrPYmRNabVK
RNLJpL8w4D44sfth5RvZ3q9t+6RTArpEtc5sh5ChzvqPOzKGMXW83C95TxmXqpbK
6olN4RevSfVjEAgCydH6HN6OhtOQEcnrU97r9H0iZOWwbw3pVrZiUkuRD1R56Wzs
2wIDAQAB
-----END PUBLIC KEY-----"""
    rsa_key = RSA.importKey(public_key)
    cipher = Cipher_pkcs1_v1_5.new(rsa_key)
    encrypted_password = cipher.encrypt(password.encode())
    return base64.b64encode(encrypted_password).decode('utf-8')

def encrypt_password_pbkdf2(password: str, salt: str = None, iterations: int = 10000) -> str:
    """
    使用PBKDF2 SHA256加密密码
    """
    if salt is None:
        # 使用密码本身作为盐值
        salt = password
    
    # 使用PBKDF2生成密钥
    key = PBKDF2(password, salt.encode(), dkLen=32, count=iterations, hmac_hash_module=hashlib.sha256)
    
    # 转换为十六进制字符串
    return key.hex()

def encrypt_password_pbkdf2_sha1(password: str, salt: str = None, iterations: int = 10000) -> str:
    """
    使用PBKDF2 SHA1加密密码
    """
    if salt is None:
        # 使用密码本身作为盐值
        salt = password
    
    # 使用PBKDF2生成密钥
    key = PBKDF2(password, salt.encode(), dkLen=32, count=iterations, hmac_hash_module=hashlib.sha1)
    
    # 转换为十六进制字符串
    return key.hex()

def encrypt_password_pbkdf2_common_salt(password: str, iterations: int = 10000) -> str:
    """
    使用PBKDF2 SHA256加密密码，使用常见盐值
    """
    # 使用第一个常见盐值
    salt = "ragforge"
    
    # 使用PBKDF2生成密钥
    key = PBKDF2(password, salt.encode(), dkLen=32, count=iterations, hmac_hash_module=hashlib.sha256)
    
    # 转换为十六进制字符串
    return key.hex()

def test_encryption():
    """测试密码加密功能"""
    test_password = "test123"
    print(f"原始密码: {test_password}")
    
    try:
        encrypted = encrypt_password(test_password)
        print(f"加密后: {encrypted}")
        print("✅ 密码加密测试成功")
        return True
    except Exception as e:
        print(f"❌ 密码加密测试失败: {e}")
        return False

def test_mmm_user_encryption():
    """测试M@M.test用户的密码加密"""
    import requests
    
    email = "M@M.test"
    password = "vPn**1234"
    url = "http://120.133.41.186/v1/user/login"
    
    # 测试不同的加密方式
    encryption_methods = [
        ("当前方法 (Base64+RSA)", encrypt_password),
        ("PBKDF2 SHA256", encrypt_password_pbkdf2),
        ("PBKDF2 SHA1", encrypt_password_pbkdf2_sha1),
        ("PBKDF2 常见盐值", encrypt_password_pbkdf2_common_salt),
        ("明文密码", encrypt_password_plain),
        ("Base64编码", encrypt_password_base64),
        ("SHA256哈希", encrypt_password_sha256),
        ("直接RSA加密", encrypt_password_direct_rsa),
    ]
    
    print(f"测试用户: {email}")
    print(f"密码: {password}")
    print("=" * 50)
    
    for method_name, encrypt_func in encryption_methods:
        try:
            encrypted_password = encrypt_func(password)
            print(f"\n测试 {method_name}:")
            print(f"加密结果: {encrypted_password[:50]}...")
            
            data = {'email': email, 'password': encrypted_password}
            response = requests.post(url, json=data)
            result = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            if result and result.get('code') == 0:
                print("✅ 登录成功！找到了正确的加密方式！")
                return method_name, encrypt_func
            else:
                print(f"❌ 登录失败: {result.get('message', '未知错误') if result else '请求失败'}")
                
        except Exception as e:
            print(f"❌ 加密失败: {e}")
    
    return None, None


if __name__ == "__main__":
    test_encryption() 