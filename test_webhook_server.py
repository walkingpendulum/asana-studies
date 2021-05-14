import hashlib
import hmac
from typing import Any

from aiohttp.client import ClientRequest, ClientResponse
from aiohttp.payload import Payload

from webhook_server import make_app


class SignedClientRequest(ClientRequest):
    """Asana sign every webhook call, so should we."""
    secret: str

    @classmethod
    def set_secret(cls, secret: str):
        cls.secret = secret

    def update_body_from_data(self, body: Any) -> None:
        super(SignedClientRequest, self).update_body_from_data(body)

        value = self.body
        if isinstance(self.body, str):
            value = self.body.encode()
        elif isinstance(self.body, Payload):
            value = self.body._value

        signature = hmac.new(
            self.secret.encode('ascii', 'ignore'),
            msg=value,
            digestmod=hashlib.sha256
        ).hexdigest()
        self.headers["X-Hook-Signature"] = signature


async def test_webhook(aiohttp_client, loop):
    webhook_url = '/receive-webhook?project=test-project'
    hook_secret = 'SECRET'

    history = []
    app = make_app(post_hook=lambda body, history=history: history.append(body))

    handshake_client = await aiohttp_client(app)
    handshake_resp: ClientResponse = await handshake_client.post(webhook_url, headers={'X-Hook-Secret': hook_secret})
    assert handshake_resp.status == 200

    webhook_payload = {
        "events": [
            {
                "user": {
                    "gid": "96185901113292",
                    "resource_type": "user"
                },
                "created_at": "2021-05-14T13:01:07.836Z",
                "action": "added",
                "resource": {
                    "gid": "1200333148959604",
                    "resource_type": "story",
                    "resource_subtype": "comment_added"
                },
                "parent": {
                    "gid": "1200261829491112",
                    "resource_type": "task",
                    "resource_subtype": "default_task"
                }
            }
        ]
    }

    SignedClientRequest.set_secret(secret=hook_secret)
    client = await aiohttp_client(app, request_class=SignedClientRequest)
    webhook_resp: ClientResponse = await client.post(webhook_url, json=webhook_payload)
    assert webhook_resp.status == 200
    assert history == [webhook_payload]


async def test_reject_untrusty_webhook(aiohttp_client, loop):
    webhook_url = '/receive-webhook?project=test-project'

    app = make_app()

    handshake_client = await aiohttp_client(app)
    handshake_resp: ClientResponse = await handshake_client.post(webhook_url, headers={'X-Hook-Secret': 'SECRET'})
    assert handshake_resp.status == 200

    SignedClientRequest.set_secret(secret='qwerty123')
    hacker = await aiohttp_client(app, request_class=SignedClientRequest)
    webhook_resp: ClientResponse = await hacker.post(webhook_url, json=[])
    assert webhook_resp.status == 400


async def test_reject_second_handshake(aiohttp_client, loop):
    webhook_url = '/receive-webhook?project=test-project'

    app = make_app()
    client = await aiohttp_client(app)

    handshake_resp: ClientResponse = await client.post(webhook_url, headers={'X-Hook-Secret': 'SECRET'})
    assert handshake_resp.status == 200

    haker_handshake_resp: ClientResponse = await client.post(webhook_url, headers={'X-Hook-Secret': 'qwerty123'})
    assert haker_handshake_resp.status == 400


async def test_reject_webhooks_before_handshake(aiohttp_client, loop):
    webhook_url = '/receive-webhook?project=test-project'

    app = make_app()

    SignedClientRequest.set_secret(secret='SECRET')
    client = await aiohttp_client(app, request_class=SignedClientRequest)
    webhook_resp: ClientResponse = await client.post(webhook_url, json=[])
    assert webhook_resp.status == 400

