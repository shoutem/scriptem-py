import os
from optparse import OptionParser
import json_api_doc
import re

def execute(plan_id, app_filter, username, password, env):
    billing_api = config.get_billing_endpoint(env)
    plan_res = network.get(*auth.as_admin(env, "{}/v1/plans/{}".format(billing_api, plan_id)))
    plan = json_api_doc.parse(plan_res.json())

    if "errors" in plan:
        print(plan["errors"][0]["detail"])
        exit(1)

    print("[{}] Adding plan {} ({} months)".format(env, plan["name"], plan["period"]["length"]))

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
    print("Plan {} will be purchased for following apps: {}{}".format(plan_id, os.linesep, apps_name_id))
    if not prompt.yes_no("Do you want to continue?"):
        exit(0)

    for app in filtered:
        purchase_plan_endpoint = "{}/v1/accounts/me/subscriptions/application:{}/actions/recurly/subscribe".format(billing_api, app["id"])
        purchase_res = network.post(*auth.as_user(username, password, env, purchase_plan_endpoint, {
            "body": json_api_doc.encode(
                data={
                    "$type": "shoutem.billing.recurly-subscribe-actions",
                    "billingInfoToken": None,
                    "plan": {
                        "$type":"shoutem.billing.plans", 
                        "id": plan_id
                    }
                })
        }))

        purchase = json_api_doc.parse(purchase_res.json())
        
        if "errors" in purchase:
            print(purchase["errors"][0]["detail"] or purchase["errors"][0]["code"])
        else:
            print("Plan purchased for {}".format(app["id"]))


def main():
    usage = "usage: %prog [options] plan_id"
    parser = OptionParser(usage)
    parser.add_option("-u", "--user",
                      help="Username of the agency owner",
                      type="string", dest="username", default="admin@agency.local")
    parser.add_option("-p", "--password",
                      help="Password of the agency owner",
                      type="string", dest="password", default="password")
    parser.add_option("-e", "--env",
                      help="Environment to run this script on, default: 'qa', options are 'prod', 'qa', 'dev', 'local'",
                      type="string", dest="env", default="qa")
    parser.add_option("-r", "--regex",
                      help="Regex to mach the application name, by default moderator will be added for every app by the specified owner",
                      type="string", dest="regex", default=".*")

    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("You must provide plan ID (for reference: Postman > Billing > Plan > Get All)")
    if options.env not in ['prod', 'qa', 'dev', 'local']:
        parser.error("Incorrect number of arguments")

    execute(args[0], options.regex, options.username, options.password, options.env)

if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from shared import network, auth, config, prompt
    main()
