# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import os

try:
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Hash import SHA256
except ImportError:
    raise ImportError('Crypto module not found. Install script.module.pycryptodome in Kodi or pycryptodome for local scripts.')

BLOCK_SIZE = 16


def _require_crypto():
    return


def _derive_keys(password, salt):
    full_key = PBKDF2(password, salt, dkLen=48, count=100000, hmac_hash_module=SHA256)
    return full_key[:16], full_key[16:]


def _aes_encrypt(plaintext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(plaintext)


def _aes_decrypt(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(ciphertext)


def _pad(data):
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len]) * pad_len


def _unpad(data):
    if not data or len(data) % BLOCK_SIZE != 0:
        raise ValueError('Invalid padding')
    pad_len = data[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError('Invalid padding')
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError('Invalid padding')
    return data[:-pad_len]


def encrypt_bytes(plaintext, password):
    _require_crypto()
    salt = os.urandom(16)
    iv = os.urandom(BLOCK_SIZE)
    enc_key, hmac_key = _derive_keys(password, salt)
    plaintext = _pad(plaintext)
    ciphertext = _aes_encrypt(plaintext, enc_key, iv)
    payload = salt + iv + ciphertext
    tag = hmac.new(hmac_key, payload, hashlib.sha256).digest()
    return payload + tag


def decrypt_bytes(blob, password):
    _require_crypto()
    if len(blob) < 16 + BLOCK_SIZE + 32:
        raise ValueError('Encrypted data is too short')
    salt = blob[:16]
    iv = blob[16:16 + BLOCK_SIZE]
    tag = blob[-32:]
    ciphertext = blob[16 + BLOCK_SIZE:-32]
    enc_key, hmac_key = _derive_keys(password, salt)
    payload = blob[:-32]
    expected_tag = hmac.new(hmac_key, payload, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_tag, tag):
        raise ValueError('Authentication failed')
    plaintext = _aes_decrypt(ciphertext, enc_key, iv)
    return _unpad(plaintext)


def encrypt_json_file(input_path, output_path, password):
    with open(input_path, 'rb') as f:
        plaintext = f.read()
    encrypted = encrypt_bytes(plaintext, password)
    with open(output_path, 'wb') as f:
        f.write(encrypted)


def decrypt_json_blob(blob, password):
    decrypted = decrypt_bytes(blob, password)
    return json.loads(decrypted.decode('utf-8'))
