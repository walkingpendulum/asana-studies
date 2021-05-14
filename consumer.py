#! /usr/bin/env python
import argparse
import json
import sys

import pika
import yaml


def read_config() -> dict:
    # keys: amqp_url
    with open('config.yaml') as f:
        return yaml.load(f, Loader=yaml.Loader)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--queue', required=True)

    return parser


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv)
    queue = args.queue

    config = read_config()
    conn_params = pika.URLParameters(url=config['amqp_url'])

    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()

    print(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body: bytes):
        print(f" [x] {json.loads(body.decode())}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue, on_message_callback=callback)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n [*] Exiting. Good bye!")
        sys.exit()


if __name__ == '__main__':
    main()
