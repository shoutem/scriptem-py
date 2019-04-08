import os
from optparse import OptionParser
import json_api_doc
import re


def execute(src_id, dest_id, app_filter, recreate_subscription, env):
    users_endpoint = config.get_auth_endpoint(env) + "/v1/realms/alias:default/users/legacyUser:{}"
    # get source and destination users, mostly for the sake of ensuring user inputed the right data
    src_user_res = network.get(*auth.as_admin(env, users_endpoint.format(src_id)))
    src_user = json_api_doc.parse(src_user_res.json())
    errors.exit_if_errors(src_user)
     
    dest_user_res = network.get(*auth.as_admin(env, users_endpoint.format(dest_id)))
    dest_user = json_api_doc.parse(dest_user_res.json())
    errors.exit_if_errors(dest_user)

    print("[{}] Transfering apps from {} to {}".format(env, src_user["username"], dest_user["username"]))

    # get all applications for the source user
    apps_endpoint = config.get_legacy_endpoint(env) + "/v1/apps"
    apps_res = network.get(*auth.as_admin(env, apps_endpoint, {
        "query": {
            "filter[owner.id]": src_id,
            "page[limit]": 99999999
        }
    }))
    apps = json_api_doc.parse(apps_res.json())
    errors.exit_if_errors(apps)    

    account_endpoint = config.get_billing_endpoint(env) + "/v1/accounts/user:{}"
    src_account_res = network.get(*auth.as_admin(env, account_endpoint.format(src_id)))
    src_account = json_api_doc.parse(src_account_res.json())
    errors.exit_if_errors(src_account)

    dest_account_res = network.get(*auth.as_admin(env, account_endpoint.format(dest_id)))
    dest_account = json_api_doc.parse(dest_account_res.json())
    errors.exit_if_errors(dest_account)

    # we don't support different account types because it's too complicated, man
    if src_account["accountType"] != dest_account["accountType"]:
        print("Source and destination account must have the same account type")
        exit(1)

    # some accounts have old application subnscription groups which could cause confusion
    if src_account["applicationPlanGroup"] != dest_account["applicationPlanGroup"]:
        print("Source and destination account must have the same application plan group")
        exit(1)

    subscription_endpoint = config.get_billing_endpoint(env) + "/v1/accounts/user:{}/subscriptions"
    src_subscriptions_res = network.get(*auth.as_admin(env, subscription_endpoint.format(src_id)))
    src_subscriptions = json_api_doc.parse(src_subscriptions_res.json())
    errors.exit_if_errors(src_subscriptions)

    # filter apps out by those that match the provided regex
    app_re = re.compile(app_filter)
    filtered = list(filter(lambda app: app_re.match(app["name"]), apps))

    apps_name_id = os.linesep.join(map(lambda app: "{} ({})".format(app["name"], app["id"]), filtered))
    print("Apps from user {} will be transfered to user {}: {}{}".format(
        src_user["username"], dest_user["username"], os.linesep, apps_name_id))
    if not prompt.yes_no("Do you want to continue?"):
        exit(0)

    # we only consider application subscription, agency transfer is not supported, just their apps
    is_valid_subscription = lambda sub, app: (
        sub["productType"] == "application"
        and sub["productId"] == app["id"]
        and sub["status"] == "subscribed"
    )
    subscribe_endpoint = config.get_billing_endpoint(env) + "/v1/accounts/{}/subscriptions/{}/actions/subscribe"
    unsubscribe_endpoint = config.get_billing_endpoint(env) + "/v1/accounts/{}/subscriptions/{}/actions/cancel"
    update_app_endpoint = config.get_legacy_endpoint(env) + "/v1/apps/{}"

    for app in filtered:
        existing_subscriptions = list(filter(lambda sub: is_valid_subscription(sub, app), src_subscriptions))

        # cancel existing subscription if it exists, we can recreate it later
        # hopefully the app owner thansfer step bellow won't fail
        if existing_subscriptions:
            subscription = existing_subscriptions[0]
            unsubscribe_res = network.post(*auth.as_admin(
                env,
                unsubscribe_endpoint.format(src_account["id"], subscription["id"]),
                { "body": json_api_doc.encode({
                    "$type": "shoutem.billing.subscriptions"
                })
            }))
            canceled_subscriptions = json_api_doc.parse(unsubscribe_res.json())
            errors.exit_if_errors(canceled_subscriptions)
            print("[{}] Canceled subscription for app {} ({})".format(env, app["id"], app["name"]))

        # .NET fails to parse included data in POST body, so we create JSON:API doc manually here
        # NodeJS services do not have this issue
        update_app_res = network.patch(*auth.as_admin(env, update_app_endpoint.format(app["id"]), {
            "body": {
                'data': {
                    'type': 'shoutem.core.application',
                    'relationships': {
                        'owner': {
                            'data': {
                                'id': dest_user["legacyId"], 
                                'type': 'shoutem.core.users'
                            }
                        }
                    }
                }
            }
        }))
        update_app = json_api_doc.parse(update_app_res.json())
        errors.exit_if_errors(update_app)
        print("[{}] Changed owner for app {} ({}) to {}".format(env, app["id"], app["name"], dest_user["username"]))

        # create a new subscription if user specified so and the previous owner had a subscription
        # this will cause new invoice on the new account, this probably won't be an issue with agencies
        if recreate_subscription and existing_subscriptions:
            subscription = existing_subscriptions[0]
            purchase_res = network.post(*auth.as_admin(env, subscribe_endpoint, {
                "body": json_api_doc.encode(
                    data={
                        "$type": "shoutem.billing.recurly-subscribe-actions",
                        "billingInfoToken": None,
                        "plan": {
                            "$type":"shoutem.billing.plans", 
                            "id": subscription["plan"]["id"]
                        }
                    })
            }))

            purchase = json_api_doc.parse(purchase_res.json())
            canceled_subscriptions = json_api_doc.parse(unsubscribe_res.json())
            errors.exit_if_errors(canceled_subscriptions)
            print("[{}] Created subscription for app {} ({}) with plan {}".format(env, app["id"], app["name"], subscription["plan"]["id"]))


def main():
    usage = "usage: %prog [options] source_account_id destination_account_id"
    parser = OptionParser(usage)
    parser.add_option("-e", "--env",
                      help="Environment to run this script on, default: 'qa', options are 'prod', 'qa', 'dev', 'local'",
                      type="string", dest="env", default="qa")
    parser.add_option("-s", "--subscribe",
                      help="Recreate the subscription on the app, True by default",
                      action="store_true", dest="subscribe", default=True)
    parser.add_option("-r", "--regex",
                      help="Regex to mach the application name, by default all apps will be transfered",
                      type="string", dest="regex", default=".*")

    (options, args) = parser.parse_args()
    
    if len(args) != 2:
        parser.error("You must provide a source and destination user id")
    if options.env not in ['prod', 'qa', 'dev', 'local']:
        parser.error("Incorrect environment {}".format(options.env))

    execute(args[0], args[1], options.regex, options.subscribe, options.env)


if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from shared import network, auth, config, prompt, errors
    main()
