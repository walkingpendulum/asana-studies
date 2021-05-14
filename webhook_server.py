#! /usr/bin/env python
import hashlib
import hmac
import json
import logging
from typing import Optional

from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')
logger.setLevel(logging.INFO)


async def receive_webhook(request: web.Request) -> web.Response:
    hook_secret: Optional[str] = request.app['asana_auth'].get('hook_secret')
    if "X-Hook-Secret" in request.headers:
        if hook_secret is not None:
            err_msg = "Second handshake request received. This could be an attacker trying to set up a new secret. " \
                      "Ignoring."
            logger.error(err_msg)
            return web.Response(status=400, reason="Can not handshake more than once")
        else:
            # Respond to the handshake request :)
            logger.info("New webhook")
            hook_secret = request.headers["X-Hook-Secret"]
            request.app['asana_auth']['hook_secret'] = hook_secret
            return web.Response(headers={"X-Hook-Secret": hook_secret})
    elif "X-Hook-Signature" in request.headers:
        # Compare the signature sent by Asana's API with one calculated locally.
        # These should match since we now share the same secret as what Asana has stored.
        content = await request.read()
        signature = hmac.new(
            (hook_secret or '').encode('ascii', 'ignore'),
            msg=content,
            digestmod=hashlib.sha256,
        ).hexdigest()
        incoming_signature = request.headers["X-Hook-Signature"].encode('ascii', 'ignore')
        if not hmac.compare_digest(signature.encode(), incoming_signature):
            logger.error("Calculated digest does not match digest from API. This event is not trusted.")
            return web.Response(status=400)

        body = await request.json()
        if not body['events']:
            # liveness probe
            return web.Response()

        logger.info(json.dumps(body, indent=4))
        post_hook = request.app['post_hook']
        if post_hook:
            post_hook(body)

        return web.Response()
    else:
        raise KeyError


def make_app(post_hook=None) -> web.Application:
    app = web.Application()
    app['asana_auth'] = {}
    app['post_hook'] = post_hook
    app.add_routes([
        web.post('/receive-webhook', receive_webhook)
    ])

    return app


if __name__ == '__main__':
    web.run_app(make_app(), port=8090)
