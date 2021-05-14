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
    channel = connection.channel()
    channel.exchange_declare(exchange='asana_comments', exchange_type='fanout')

    queue_args = {
        'x-max-length': 100000,
        "x-message-ttl": 604800000,
    }
    due_time_q = channel.queue_declare(queue='due_time_worker', arguments=queue_args)
    photos_number_q = channel.queue_declare(queue='photos_number_worker', arguments=queue_args)

    channel.queue_bind(exchange='asana_comments', queue=due_time_q.method.queue)
    channel.queue_bind(exchange='asana_comments', queue=photos_number_q.method.queue)
