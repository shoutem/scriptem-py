import base64
import json
import os
import json_api_doc
from . import config, network

tokens = {}

def as_user(username, password, env, uri, opts={}):
    if (username, env) not in tokens:
        token_endpoint = "{}/v1/tokens".format(config.get_auth_endpoint(env))
        creds = base64.b64encode("{}:{}".format(username, password).encode("UTF-8")).decode("UTF-8")
        refresh_response = network.post(token_endpoint, {
            "headers": {
                "Authorization": "Basic {}".format(creds)
            },
            "body": json_api_doc.encode({
                "$type": "shoutem.auth.tokens"
            })
        })
        
        parsed_refresh = json_api_doc.parse(refresh_response.json())
        
        access_response = network.post(token_endpoint, {
            "headers": {
                "Authorization": "Bearer {}".format(parsed_refresh["token"])
            },
            "body": json_api_doc.encode({
                "$type": "shoutem.auth.tokens",
                "tokenType": "access-token",
                "subjectType": "user"
            })
        })

        access_parsed = json_api_doc.parse(access_response.json())
        tokens[(username, env)] = access_parsed["token"]

    opts.setdefault("headers", {})["Authorization"] = "Bearer {}".format(tokens[(username, env)])
    return uri, opts

def as_admin(env, uri, opts):
    opts.setdefault("headers", {})["Authorization"] = config.get_admin_token(env)
    return uri, opts