import os

import asana
import json
import argparse


personal_access_token = os.environ['TEMP_PAT']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("task_gid")

    args = parser.parse_args()

    client = asana.Client.access_token(personal_access_token)
    client.options['client_name'] = "hello_world_python"

    result = client.stories.get_stories_for_task(args.task_gid)
    comments = [story for story in result if story["type"] == "comment"]
    print(json.dumps(comments, indent=4))
