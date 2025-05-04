import hmac, hashlib, secrets, os

HEADER = os.getenv("SIGNATURE_HEADER", "X-Webhook-Signature")
ALGO   = os.getenv("SIGN_ALGO", "sha256")

def sign(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), body, getattr(hashlib, ALGO)).hexdigest()
    return f"{ALGO}={digest}"

def compare(sig1: str, sig2: str) -> bool:
    # constant‑time compare, strip possible scheme prefix
    return secrets.compare_digest(sig1.split("=",1)[-1], sig2.split("=",1)[-1])
