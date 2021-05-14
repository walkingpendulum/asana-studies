#! /usr/bin/env python
import pika
import yaml
import time


def read_config() -> dict:
    # keys: amqp_url
    with open('config.yaml') as f:
        return yaml.load(f, Loader=yaml.Loader)


if __name__ == '__main__':
    config = read_config()
    conn_params = pika.URLParameters(url=config['amqp_url'])
    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()
    channel.exchange_declare(exchange='asana_comments', exchange_type='fanout')

    for i in range(10):
        msg = f'Test message {i}.'
        channel.basic_publish(exchange='asana_comments', routing_key='', body=msg.encode())
        print(f'Published: {msg}')
        time.sleep(0.5)

    connection.close()
