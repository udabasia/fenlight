#!/usr/bin/env python3
import argparse
import hashlib
import hmac
import os
import sys

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
    """Derive encryption and HMAC keys from password using PBKDF2."""
    full_key = PBKDF2(password, salt, dkLen=48, count=100000, hmac_hash_module=SHA256)
    return full_key[:16], full_key[16:]


def _aes_encrypt(plaintext, key, iv):
    """Encrypt plaintext using AES-CBC."""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(plaintext)


def _pad(data):
    """Apply PKCS7 padding to data."""
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len]) * pad_len


def encrypt_bytes(plaintext, password):
    """Encrypt bytes with password using AES-CBC and HMAC-SHA256."""
    # Ensure password is bytes
    if isinstance(password, str):
        password = password.encode('utf-8')
    salt = os.urandom(16)
    iv = os.urandom(BLOCK_SIZE)
    enc_key, hmac_key = _derive_keys(password, salt)
    plaintext = _pad(plaintext)
    ciphertext = _aes_encrypt(plaintext, enc_key, iv)
    payload = salt + iv + ciphertext
    tag = hmac.new(hmac_key, payload, hashlib.sha256).digest()
    return payload + tag


def main():
    parser = argparse.ArgumentParser(description='Encrypt a secrets JSON file for Kodi updater use.')
    parser.add_argument('input', help='Path to the plain JSON secrets file')
    parser.add_argument('output', nargs='?', default='secrets.json.enc', help='Output encrypted file path')
    parser.add_argument('--password', help='Password to encrypt the file with')
    args = parser.parse_args()

    if args.password:
        password = args.password
    else:
        password = input('Secret password: ')
        if not password:
            raise SystemExit('Password is required')

    with open(args.input, 'rb') as f:
        plaintext = f.read()

    encrypted = encrypt_bytes(plaintext, password)

    with open(args.output, 'wb') as f:
        f.write(encrypted)

    print('Encrypted secrets written to:', args.output)


if __name__ == '__main__':
    main()
