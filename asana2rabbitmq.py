#! /usr/bin/env python
import asyncio
import json
from typing import List, Dict

import aio_pika
import yaml
from aiohttp import web

import webhook_server


def read_config() -> dict:
    # keys: amqp_url
    with open('config.yaml') as f:
        return yaml.load(f, Loader=yaml.Loader)


async def connect_rabbitmq(app: web.Application):
    loop = asyncio.get_event_loop()
    connection = await aio_pika.connect_robust(app['config']['amqp_url'], loop=loop)

    channel: aio_pika.Channel = await connection.channel()
    exchange: aio_pika.Exchange = await channel.declare_exchange(name='asana_events', type='topic')

    app['rabbitmq_exchange'] = exchange
    app['rabbitmq_connection'] = connection


async def close_rabbitmq(app: web.Application):
    await app['rabbitmq_connection'].close()


async def publish_to_rabbitmq(app: web.Application, body: Dict[str, List[dict]]):
    exchange: aio_pika.Exchange = app['rabbitmq_exchange']

    for event in body['events']:
        resource = event['resource']
        msg = aio_pika.Message(body=json.dumps(event).encode(), content_type="application/json")
        routing_key = '.'.join([resource['resource_type'], resource['resource_subtype'], event['action']])
        await exchange.publish(msg, routing_key=routing_key)


def make_app() -> web.Application:
    app = webhook_server.make_app(post_hook=publish_to_rabbitmq)

    app['config'] = read_config()

    app.on_startup.append(connect_rabbitmq)
    app.on_cleanup.append(close_rabbitmq)
    return app


if __name__ == '__main__':
    web.run_app(make_app(), port=8090)
