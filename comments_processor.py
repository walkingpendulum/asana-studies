#! /usr/bin/env python
import argparse
import json
import sys

import asana
import pika
import yaml


def read_config() -> dict:
    # keys: amqp_url
    with open('config.yaml') as f:
        return yaml.load(f, Loader=yaml.Loader)


def make_client(config: dict):
    client = asana.Client.access_token(config['pat'])

    # Be nice to Asana and let them know you're running this example.
    # This is optional, and you can delete this line.
    client.options['client_name'] = "https://github.com/walkingpendulum/asana-studies"

    return client


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

    asana_client = make_client(config)

    print(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body: bytes):
        event = json.loads(body.decode())
        comment_data = asana_client.stories.get_story(event["resource"]["gid"])

        print(f" [x] {json.dumps(comment_data)}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue, on_message_callback=callback)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n [*] Exiting. Good bye!")
        sys.exit()


if __name__ == '__main__':
    main()
