#! /usr/bin/env python
import pika
import yaml


def read_config() -> dict:
    # keys: amqp_url
    with open('config.yaml') as f:
        return yaml.load(f, Loader=yaml.Loader)


if __name__ == '__main__':
    config = read_config()
    conn_params = pika.URLParameters(url=config['amqp_url'])

    connection = pika.BlockingConnection(conn_params)
    ch = connection.channel()
    exchange_name = 'asana_events'
    ch.exchange_declare(exchange=exchange_name, exchange_type='topic')

    queue_args = {
        'x-max-length': 100000,
        "x-message-ttl": 604800000,
    }
    comments_q = ch.queue_declare(queue='comments', arguments=queue_args)
    tasks_q = ch.queue_declare(queue='task_changes', arguments=queue_args)

    ch.queue_bind(exchange=exchange_name, queue=comments_q.method.queue, routing_key='story.comment_added.added')
    ch.queue_bind(exchange=exchange_name, queue=tasks_q.method.queue, routing_key='task.default_task')
