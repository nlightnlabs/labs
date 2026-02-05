import bcrypt
import hashlib
import os
import base64

def hash_text(text=None, method="bcrypt"):
    if text is None:
        return None

    if method == "bcrypt":
        return bcrypt.hashpw(text.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    elif method == "sha256":
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    elif method == "sha512":
        return hashlib.sha512(text.encode("utf-8")).hexdigest()

    elif method == "pbkdf2":
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', text.encode('utf-8'), salt, 100000)
        return base64.b64encode(salt + key).decode('utf-8')  # salt + key for later verification

    else:
        raise ValueError(f"Unsupported encryption method: {method}")



def match_encrypted_text(text=None, encrypted_text=None, method="bcrypt"):
    if text is None or encrypted_text is None:
        return False

    if method == "bcrypt":
        return bcrypt.checkpw(text.encode("utf-8"), encrypted_text.encode("utf-8"))

    elif method == "sha256":
        return hashlib.sha256(text.encode("utf-8")).hexdigest() == encrypted_text

    elif method == "sha512":
        return hashlib.sha512(text.encode("utf-8")).hexdigest() == encrypted_text

    elif method == "pbkdf2":
        decoded = base64.b64decode(encrypted_text.encode("utf-8"))
        salt = decoded[:16]
        original_key = decoded[16:]
        new_key = hashlib.pbkdf2_hmac('sha256', text.encode('utf-8'), salt, 100000)
        return new_key == original_key

    else:
        raise ValueError(f"Unsupported encryption method: {method}")
