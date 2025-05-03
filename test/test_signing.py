from app.signing import sign, verify, HEADER_NAME

def test_roundtrip():
    secret = "tok"
    body   = b'{"x":1}'
    sig = sign(secret, body)
    assert verify(secret, body, sig)

def test_constant_header_name():
    assert HEADER_NAME.startswith("X-")
