#! /usr/bin/env python
import argparse
import json

import asana
import yaml


def read_config():
    # keys: pat, workspace
    with open('config.yaml') as f:
        return yaml.load(f, Loader=yaml.Loader)


def make_client(config):
    client = asana.Client.access_token(config['pat'])

    # Be nice to Asana and let them know you're running this example.
    # This is optional, and you can delete this line.
    client.options['client_name'] = "https://github.com/walkingpendulum/asana-studies/blob/master/asana_cli.py"

    return client


def make_parser():
    parser = argparse.ArgumentParser()
    commands_group = parser.add_subparsers(
        title='Available Asana resources to manage',
        description='Resources that Asana API provides.',
        help='Additional help for available resources',
        dest='resource',
    )
    webhooks_commands_parser = commands_group.add_parser(
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

    pak_create_parser = webhooks_commands_parser_group.add_parser('list', description='List all webhooks')
    pak_create_parser.add_argument(
        '--workspace',
        help='Webhooks would be listed within given workspace. If omitted, value from config will be used',
    )

    return parser


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv)

    if args.resource == 'webhooks':
        manage_webhooks(args)


def list_webhooks(workspace: str, client):
    webhooks = list(client.webhooks.get_all(workspace=workspace))
    return webhooks


def manage_webhooks(args: argparse.Namespace):
    command = args.webhooks_command
    workspace = args.workspace

    config = read_config()
    client = make_client(config)
    workspace = workspace or config['workspace']

    if command == 'list':
        webhooks = list_webhooks(workspace=workspace, client=client)
        print(json.dumps(webhooks, indent=4))


if __name__ == '__main__':
    main()
