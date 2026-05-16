# FenLight Kodi Repo

This repository contains the FenLight Kodi addon and repository packaging files.

## Secret file workflow

For secure secret delivery, `plugin.video.fenlight` now downloads an encrypted secret file from the repository and decrypts it after the user enters a password.

### How it works

- The addon downloads `secrets.json.enc` from the repo.
- The user is prompted for a password in Kodi.
- The addon decrypts the file and loads the JSON contents.
- The password is validated against a saved SHA256 hash in the addon settings.

### Encrypting secrets before publishing

Use `encrypt_secrets.py` from the repo root to encrypt a plain JSON file:

```bash
python encrypt_secrets.py path/to/secrets.json secrets.json.enc
```

Then upload `secrets.json.enc` to your repository.

### Crypto module requirement

The addon requires `script.module.pycryptodome` in Kodi and uses the `Crypto` API internally.

- Add `<import addon="script.module.pycryptodome" version="3.4.3" />` to the addon requirements.
- If you run `encrypt_secrets.py` locally, install `pycryptodome` in that Python environment.

If this module is missing, encrypted secrets cannot be decrypted.

### Development environment

To set up a local virtual environment for encrypting secrets prior to committing:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
uv install -r requirements-dev.txt
```

Then run:

```powershell
python encrypt_secrets.py secrets.json secrets.json.enc
```

## Files added

- `README.md` — this documentation
- `encrypt_secrets.py` — command-line helper to encrypt secrets
- `plugin.video.fenlight/resources/lib/modules/crypto_utils.py` — crypto helper supporting optional external crypto libraries
- `plugin.video.fenlight/resources/lib/modules/updater.py` — updated `get_secrets()` to decrypt `secrets.json.enc`

## Important notes

- This is not a replacement for a proper secure server.
- Keep the decryption password secret and do not store it in plain text.
- The encrypted file is safe to publish, but the password must remain private.
