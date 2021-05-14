# asana-studies

## webhooks studies
1. Install grok tool. `brew install ngrok` for MacOS users. Follow instructions on https://dashboard.ngrok.com/get-started/your-authtoken to configure it.
1. Run `ngrok http 8090`. This will block, so do this in a separate terminal window.
1. Copy the subdomain, e.g. e91dadc7
1. Create a new PAT - we're going to use ngrok on prod Asana, and don't want to give it long-term middleman access. Follow instructions on https://app.asana.com/-/developer_console.
1. Add this PAT to the local config
    ```bash
    echo 'pat: "your_private_access_token_here"' >> config.yaml 
   ```
1.  Add the Asana workspace to the local config (this is required for webhooks.get_all). You could get workspace id from url in admin console of Asana UI.
    ```bash
    echo 'workspace: your_workspace_id_here' >> config.yaml 
    ```
1. Run `./webhook_server.py`. This will block, so do this in a separate terminal window.
1. Request Asana to create webhook
   ```bash
   ./asana-cli.py webhooks create --target 'https://SUBDOMAIN_HERE.ngrok.io/receive-webhook?project=PROJECT_ID' --resource PROJECT_ID
   ```
1. Make changes in Asana and see the logs from the returned webhooks.
1. Don't forget to deauthorize your temp PAT when you're done.

## asana2rabbitmq
This is an extension of the asana studies that were described above. Please familiarize yourself with them before continue.

1. Acquire running RabbitMQ instance.
1. Add `amqp_url: amqps://login:passwod@host:port` entry to `config.json`.
1. Run `./asana2rabbitmq.py`
1. Register webhook via `asana-cli.py`
1. Run `./listen.py --queue task_changes` and `./listen.py --queue comments`. This will block, so do this in a separate terminal windows.
