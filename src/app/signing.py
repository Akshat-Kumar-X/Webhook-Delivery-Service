import hmac, hashlib, secrets

HEADER_NAME = "X-Webhook-Signature"
ALGORITHM = "sha256"

def sign(secret: str, body_bytes: bytes) -> str:
    mac = hmac.new(secret.encode(), body_bytes, hashlib.sha256)
    return mac.hexdigest()

def compare(sig_a: str, sig_b: str) -> bool:
    # Constant‑time compare
    return secrets.compare_digest(sig_a, sig_b)
