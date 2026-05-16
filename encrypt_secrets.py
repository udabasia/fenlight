#!/usr/bin/env python3
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(ROOT, 'plugin.video.fenlight', 'resources', 'lib')
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

try:
    from modules.crypto_utils import encrypt_bytes
except ImportError:
    raise ImportError('Unable to import crypto_utils. Ensure the script is run from the repository root.')


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
