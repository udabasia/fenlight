# -*- coding: utf-8 -*-
"""Crypto utilities for Fen Light secrets handling."""

import hashlib
import hmac
import json

try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Protocol.KDF import PBKDF2
    from Cryptodome.Hash import SHA256
except ImportError:
    try:
        from Crypto.Cipher import AES
        from Crypto.Protocol.KDF import PBKDF2
        from Crypto.Hash import SHA256
    except ImportError:
        raise ImportError('Crypto module not found. Install pycryptodome to use this script.')

BLOCK_SIZE = 16


def _derive_keys(password, salt):
    """Derive AES encryption key and HMAC key from password and salt."""
    full_key = PBKDF2(password, salt, dkLen=48, count=100000, hmac_hash_module=SHA256)
    return full_key[:16], full_key[16:]


def _unpad(data):
    """Remove PKCS7 padding from decrypted data."""
    if not data or len(data) % BLOCK_SIZE != 0:
        raise ValueError('Invalid padded data length')
    pad_len = data[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError('Invalid padding bytes')
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError('Invalid PKCS7 padding')
    return data[:-pad_len]


def decrypt_json_blob(blob, password):
    """Decrypt an AES-encrypted JSON blob using the provided password.

    The expected blob format is:
        salt (16 bytes) || iv (16 bytes) || ciphertext || hmac-tag (32 bytes)

    The key material is derived with PBKDF2(password, salt, dkLen=48, count=100000,
    hmac_hash_module=SHA256). The first 16 bytes are the AES key and the remainder
    is the HMAC key.
    """
    if isinstance(password, str):
        password = password.encode('utf-8')

    if len(blob) < 16 + 16 + 32:
        raise ValueError('Encrypted blob is too short to contain required fields')

    salt = blob[0:16]
    iv = blob[16:32]
    tag = blob[-32:]
    ciphertext = blob[32:-32]


    enc_key, hmac_key = _derive_keys(password, salt)

    payload = salt + iv + ciphertext
    expected_tag = hmac.new(hmac_key, payload, hashlib.sha256).digest()

    if not hmac.compare_digest(expected_tag, tag):
        raise ValueError('Invalid password or corrupted data')

    cipher = AES.new(enc_key, AES.MODE_CBC, iv)

    plaintext = cipher.decrypt(ciphertext)

    plaintext = _unpad(plaintext)


    return json.loads(plaintext.decode('utf-8'))
