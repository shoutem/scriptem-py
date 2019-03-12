import os
from optparse import OptionParser
import json_api_doc

def get_attr(obj, path):
    split_path = path.split(".")
    for p in split_path:
        obj = obj[p]

    return obj


def execute(username, password, name, count, env):
    print("[{}] Creating {} new app(s) for user {}".format(env, count, username))
    if not prompt.yes_no("Do you want to continue?"):
        exit(0)

    # create new apps by cloning the base app
    endpoint = config.get_apps_endpoint(env) + "/v1/apps/base/actions/clone"
    for i in range(count):
        app_name = "{} {}".format(name, i + 1) if count > 1 else name
        body = json_api_doc.encode({
            "$type": "shoutem.core.application-clones",
            "name": app_name,
            "alias": "base"
        })

        res = network.post(*auth.as_user(username, password, env, endpoint, { "body": body }))
        res_parsed = json_api_doc.parse(res.json())
        print(res_parsed["id"])


def main():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-c", "--count",
                      help="Number of apps to create",
                      type="int", dest="count", default=1)
    parser.add_option("-u", "--user",
                      help="Username of the new app owner",
                      type="string", dest="username", default="admin@agency.local")
    parser.add_option("-p", "--password",
                      help="Password of the new app owner",
                      type="string", dest="password", default="password")
    parser.add_option("-t", "--title",
                    help="New app title, if count is larger then 1 it will be numbered, ie. Your app name 1, Your app name 2...",
                    type="string", dest="title", default="New App")
    parser.add_option("-e", "--env",
                      help="Environment to run this script on, default: 'qa', options are 'prod', 'qa', 'dev'",
                      type="string", dest="env", default="qa")
    
    (options, args) = parser.parse_args()
    
    if len(args) != 0:
        parser.error("Too many arguments")
    if options.env not in ['prod', 'qa', 'dev']:
        parser.error("Incorrect environment {}".format(options.env))

    execute(options.username, options.password, options.title,  options.count, options.env)

if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from shared import network, auth, config, prompt
    main()
