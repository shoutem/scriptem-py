import os
from optparse import OptionParser
import requests
import json
import json_api_doc

def get_attr(obj, path):
    split_path = path.split(".")
    for p in split_path:
        obj = obj[p]

    return obj

def execute(app_id, limit, env):
    endpoint = config[env]['auth_endpoint']
    json_url = 'https://{}/v1/realms/externalReference:{}/users?page%5Blimit%5D={}'.format(endpoint, app_id, limit)

    fields = ['id', 'legacyId', 'username', 'profile.nick']
    input_json = requests.get(json_url).json()

    print(','.join(fields))

    for d in json_api_doc.parse(input_json):
        attributes = [ get_attr(d, attr) for attr in fields ]
        print(','.join(attributes))


def main():
    usage = "usage: %prog [options] app_id"
    parser = OptionParser(usage)
    parser.add_option("-l", "--limit",
                      help="Maximum number of users to get",
                      type="int", dest="limit", default=100000)
    parser.add_option("-e", "--env",
                      help="Environment to run this script on, options are 'prod', 'qa', 'dev'",
                      type="string", dest="env", default="qa")
    
    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("Incorrect number of arguments")
    if options.env not in ['prod', 'qa', 'dev']:
        parser.error("Incorrect number of arguments")

    execute(args[0], options.limit, options.env)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(script_dir, '..', 'config', 'config.json')) as f:
        config = json.load(f)

    try: 
        with open(os.path.join(script_dir, '..', 'config', 'tokens.json')) as f:
            tokens = json.load(f)
    except IOError:
        tokens = {}

    main()