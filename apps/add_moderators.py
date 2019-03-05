import os
from optparse import OptionParser
import json_api_doc
import re

def execute(moderator_email, moderator_password, app_filter, username, password, env):
    print("[{}] Adding moderator {}".format(env, moderator_email))

    # get the agency for the provided owner
    agency_endpoint = config.get_apps_endpoint(env) + "/v1/agencies/mine"
    agency_res = network.get(*auth.as_user(username, password, env, agency_endpoint))
    agency = json_api_doc.parse(agency_res.json())

    # get existing moderators for agency
    moderators_endpoint = config.get_apps_endpoint(env) + "/v1/moderators"
    moderators_res = network.get(*auth.as_user(username, password, env, moderators_endpoint, { 
        "query": {
            "filter[agency]": agency["id"],
            "page[limit]": 99999999
        }
    }))
    moderators = json_api_doc.parse(moderators_res.json())
    existing_moderator = list(filter(lambda mod: mod["user"]["username"] == moderator_email, moderators))

    # create a new moderator for agency if one does not exist already
    if not existing_moderator and prompt.yes_no("Moderator does not exist. Do you want to create it?"): 
        create_moderator_endpoint = config.get_apps_endpoint(env) + "/v1/moderators/actions/create-for-user"
        create_moderator_res = network.post(*auth.as_user(username, password, env, create_moderator_endpoint, {
            "body": json_api_doc.encode({
                "$type": "shoutem.core.moderator-users",
                "password": moderator_password,
                "username": moderator_email,
                "agency": {
                    "$type":"shoutem.core.agencies",
                    "id": agency["id"]
                }
            })
        }))
        
        try:
            moderator = json_api_doc.parse(create_moderator_res.json())
        except AttributeError:
            raise Exception("User with such email/password already exists")
    else:
        moderator = existing_moderator[0]

    # get all applications for the provided owner(username, password)
    apps_endpoint = config.get_apps_endpoint(env) + "/v1/apps"
    apps_res = network.get(*auth.as_user(username, password, env, apps_endpoint, {
        "query": {
            "page[limit]": 99999999
        }
    }))
    apps = json_api_doc.parse(apps_res.json())

    # filter apps out by those that match the provided regex
    app_re = re.compile(app_filter)
    filtered = list(filter(lambda app: app_re.match(app["name"]), apps))

    apps_name_id = os.linesep.join(map(lambda app: "{} ({})".format(app["name"], app["id"]), filtered))
    print("Moderator {} will be added to following apps: {}{}".format(moderator_email, os.linesep, apps_name_id))
    if not prompt.yes_no("Do you want to continue?"):
        exit(0)

    for app in filtered:
        add_moderator_endpoint = "{}/{}/moderated-applications".format(moderators_endpoint, moderator["id"])
        moderator_res = network.post(*auth.as_user(username, password, env, add_moderator_endpoint, {
            "body": json_api_doc.encode({
                "$type": "shoutem.core.moderator-applications",
                "role": "content-editor",
                "application": {
                    "$type":"shoutem.core.applications", 
                    "id": app["id"]
                }
            })
        }))

        try:
            json_api_doc.parse(moderator_res.json())
            print("Moderator added for {}".format(app["id"]))
        except AttributeError:
            print("Moderator already exists for {}".format(app["id"]))


def main():
    usage = "usage: %prog [options] moderator_username moderator_password"
    parser = OptionParser(usage)
    parser.add_option("-u", "--user",
                      help="Username of the agency owner",
                      type="string", dest="username", default="admin@agency.local")
    parser.add_option("-p", "--password",
                      help="Password of the agency owner",
                      type="string", dest="password", default="password")
    parser.add_option("-e", "--env",
                      help="Environment to run this script on, default: 'qa', options are 'prod', 'qa', 'dev'",
                      type="string", dest="env", default="qa")
    parser.add_option("-r", "--regex",
                      help="Regex to mach the application name, by default moderator will be added for every app by the specified owner",
                      type="string", dest="regex", default=".*")

    (options, args) = parser.parse_args()
    
    if len(args) != 2:
        parser.error("You must provide moderator username and password")
    if options.env not in ['prod', 'qa', 'dev']:
        parser.error("Incorrect number of arguments")

    execute(args[0], args[1], options.regex, options.username, options.password, options.env)

if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from shared import network, auth, config, prompt
    main()
