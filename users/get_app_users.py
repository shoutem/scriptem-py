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
    endpoint = config.get_auth_endpoint(env)
    json_url = '{}/v1/realms/externalReference:{}/users?page%5Blimit%5D={}'.format(endpoint, app_id, limit)

    fields = ['id', 'legacyId', 'username', 'profile.nick']
    input_json = requests.get(json_url).json()

    print(','.join(fields))

    for d in json_api_doc.deserialize(input_json):
        attributes = [ get_attr(d, attr) for attr in fields ]
        print(','.join(attributes))


def main():
    usage = "usage: %prog [options] app_id"
    parser = OptionParser(usage)
    parser.add_option("-l", "--limit",
                      help="Maximum number of users to get",
                      type="int", dest="limit", default=100000)
    parser.add_option("-e", "--env",
                      help="Environment to run this script on, default: 'qa', options are 'prod', 'qa', 'dev', 'local'",
                      type="string", dest="env", default="qa")
    
    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("You must provide app_id")
    if options.env not in ['prod', 'qa', 'dev', 'local']:
        parser.error("Incorrect environment {}".format(options.env))

    execute(args[0], options.limit, options.env)

if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from shared import network, auth, config
    main()
