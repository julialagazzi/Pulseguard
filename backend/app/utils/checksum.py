import hashlib

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_file(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
