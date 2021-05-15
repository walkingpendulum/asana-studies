#! /usr/bin/env python
import argparse
import json
from typing import List

import asana
import yaml


def read_config() -> dict:
    # keys: pat, workspace
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
    resources_group = parser.add_subparsers(
        title='Available Asana resources to manage',
        description='Resources that Asana API provides.',
        help='Additional help for available resources',
        dest='asana_resource',
    )
    webhooks_commands_parser = resources_group.add_parser(
        'webhooks',
        description='Webhooks management commands, supported by Asana API',
        help='Additional help for available webhooks management commands',
    )
    webhooks_commands_parser_group = webhooks_commands_parser.add_subparsers(
        title='Webhooks management commands',
        description='Create, list, or delete webhooks.',
        help='Additional help for available commands',
        dest='webhooks_command',
    )

    webhook_list_parser = webhooks_commands_parser_group.add_parser('list', description='List all webhooks')
    webhook_list_parser.add_argument(
        '--workspace',
        help='Webhooks would be listed within given workspace. If omitted, value from config will be used',
    )

    webhook_create_parser = webhooks_commands_parser_group.add_parser('create', description='Create webhook')
    webhook_create_parser.add_argument(
        '--resource',
        help='A resource ID to subscribe to. The resource can be a task or project.',
        required=True,
    )

    webhook_create_parser.add_argument('--target', help='The URL to receive the HTTP POST.')

    webhook_delete_parser = webhooks_commands_parser_group.add_parser('delete', description='Delete webhook')
    webhook_delete_parser.add_argument(
        '--webhook-id',
        help='The webhook to delete.',
        required=True,
    )

    return parser


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv)

    if args.asana_resource == 'webhooks':
        manage_webhooks(args)


def list_webhooks(workspace: str, client) -> List[dict]:
    webhooks = list(client.webhooks.get_all(workspace=workspace))
    return webhooks


def create_webhook(resource: str, target: str, client) -> dict:
    webhook = client.webhooks.create(resource=resource, target=target)
    return webhook


def delete_webhook(webhook_id: str, client):
    client.webhooks.delete_by_id(webhook_id)


def manage_webhooks(args: argparse.Namespace):
    command = args.webhooks_command

    config = read_config()
    client = make_client(config)

    if command == 'list':
        workspace = args.workspace or config['workspace']
        webhooks = list_webhooks(workspace=workspace, client=client)
        print(json.dumps(webhooks, indent=4))

    if command == 'create':
        resource = args.resource
        target = args.target
        webhook = create_webhook(client=client, resource=resource, target=target)
        print(json.dumps(webhook, indent=4))

    if command == 'delete':
        webhook_id = args.webhook_id
        delete_webhook(client=client, webhook_id=webhook_id)


if __name__ == '__main__':
    main()
