#! /usr/bin/env python
import asyncio

import aio_pika
import yaml


def read_config() -> dict:
    # keys: amqp_url
    with open('config.yaml') as f:
        return yaml.load(f, Loader=yaml.Loader)


async def main(loop):
    config = read_config()
    connection = await aio_pika.connect_robust(config['amqp_url'], loop=loop)

    channel: aio_pika.Channel = await connection.channel()
    exchange: aio_pika.Exchange = await channel.declare_exchange(name='asana_comments', type='fanout')

    for i in range(10):
        msg = f'Test message {i}.'
        await exchange.publish(aio_pika.Message(body=msg.encode()), routing_key='')

        print(f'Published: {msg}')
        await asyncio.sleep(0.8)

    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
