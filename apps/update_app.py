import os
from optparse import OptionParser
import json_api_doc
import re

def execute(extensions_with_version, app_filter, user, env):
    apps_res = network.get(*auth.as_admin(env, "{}/v1/apps/".format(config.get_legacy_endpoint(env)), {
        "query": {
            "filter[owner.id]": user,
        }
    }))
    apps = json_api_doc.parse(apps_res.json())
    errors.exit_if_errors(apps)

    # filter apps out by those that match the provided regex
    app_re = re.compile(app_filter)
    filtered = list(filter(lambda app: app_re.match(app["name"]), apps))

    apps_name_id = os.linesep.join(map(lambda app: "{} ({})".format(app["name"], app["id"]), filtered))
    print("[{}] Updating for following apps: {}{}".format(env, os.linesep, apps_name_id))
    if not prompt.yes_no("Do you want to continue?"):
        exit(0)

    extension_re = re.compile("(.*)@(.*)")
    extension_name_ids = []
    extensions_endpoint = config.get_extension_endpoint(env)
    for extension in extensions_with_version:
        match_res = extension_re.match(extension)
        if len(match_res.groups()) != 2:
            print("Invalid extension name@version: {}".format(extension))
            exit(1)
        
        extension_name = match_res.group(1)
        extension_version = match_res.group(2)
        extension_res = network.get(*auth.as_admin(env, "{}/v1/extensions".format(extensions_endpoint), {
            "query": {
                "filter[canonicalName]": extension_name,
                "filter[version]": extension_version,
            }
        }))
        extensions = json_api_doc.parse(extension_res.json())
        errors.exit_if_errors(extensions)

        if len(extensions) == 0:
            print("No extension {}".format(extension))
            exit(1)
        
        extension_name_ids += [(extension_name, extensions[0]["id"])]

    apps_endpoint = config.get_apps_endpoint(env)
    for app in filtered:
        app_installations_res = network.get(*auth.as_admin(env, "{}/v1/apps/{}/installations".format(apps_endpoint, app["id"])))
        app_installations = json_api_doc.parse(app_installations_res.json())
        errors.exit_if_errors(app_installations)

        for extension_name, extension_id in extension_name_ids:
            current_installations = list(filter(lambda i: i["canonicalName"] == extension_name, app_installations))
            if len(current_installations) == 0:
                print("SKIPPING extension installation {} for app {}. {}".format(extension_name, app["id"], "Extension must be installed"))
                continue

            current_installation = current_installations[0]

            update_extension_endpoint = "{}/v1/apps/{}/installations/{}".format(apps_endpoint, app["id"], current_installation["id"])
            update_res = network.patch(*auth.as_admin(env, update_extension_endpoint, {
                "body": json_api_doc.encode(
                    data={
                        "$type": "shoutem.core.installations",
                        "id": current_installation["id"],
                        "extension": extension_id
                    })
            }))

            update_res = json_api_doc.parse(update_res.json())
            errors.exit_if_errors(update_res)
                
            print("Extension installation {} updated for app {}".format(extension_name, app["id"]))


def main():
    usage = "usage: %prog [options] plan_id"
    parser = OptionParser(usage)
    parser.add_option("-u", "--user",
                      help="ID of user/agency",
                      type="string", dest="user", default="3")
    parser.add_option("-e", "--env",
                      help="Environment to run this script on, default: 'qa', options are 'prod', 'qa', 'dev', 'local'",
                      type="string", dest="env", default="qa")
    parser.add_option("-r", "--regex",
                      help="Regex to mach the application name, by default moderator will be added for every app by the specified owner",
                      type="string", dest="regex", default=".*")

    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.error("You must provide atleast one extension")
    if options.env not in ['prod', 'qa', 'dev', 'local']:
        parser.error("Incorrect number of arguments")

    execute(args, options.regex, options.user, options.env)

if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from shared import network, auth, config, prompt, errors
    main()
