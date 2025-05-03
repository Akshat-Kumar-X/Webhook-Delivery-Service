import json, uuid
import pytest
from unittest.mock import patch, MagicMock

from app.tasks import deliver_webhook
from app.db import SessionLocal
from app import models
from app.signing import HEADER_NAME, sign

@pytest.fixture
def sub_and_req():
    db = SessionLocal()
    sub = models.Subscription(
        id=uuid.uuid4(),
        target_url="https://example.com/wh",
        secret="tok",
        event_types=None,
    )
    req = models.WebhookRequest(id=uuid.uuid4(), subscription=sub, payload={"a": 1})
    db.add_all([sub, req]); db.commit()
    return str(req.id), sub.secret, req.payload

def test_header_added(sub_and_req):
    req_id, secret, payload = sub_and_req

    with patch("app.tasks.httpx.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        deliver_webhook(req_id)       # synchronous call inside test

    mock_post.assert_called_once()
    headers = mock_post.call_args.kwargs["headers"]
    expected = sign(secret, json.dumps(payload, separators=(",", ":")).encode())
    assert headers[HEADER_NAME] == expected
