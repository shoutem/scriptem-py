import os
import json

def get_config(env):
    try: 
        script_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(script_dir, '..', 'config', 'config.json')) as f:
            return json.load(f)[env]
    except IOError:
        raise Exception("Missing config/config.json")

def get_auth_endpoint(env):
    return get_config(env)["auth_endpoint"]


def get_apps_endpoint(env):
    return get_config(env)["app_endpoint"]


def get_extension_endpoint(env):
    return get_config(env)["extension_endpoint"]


def get_billing_endpoint(env):
    return get_config(env)["billing_endpoint"]


def get_loyalty_endpoint(env):
    return get_config(env)["loyalty_endpoint"]


def get_legacy_endpoint(env):
    return get_config(env)["legacy_endpoint"]


def get_admin_token(env):    
    try: 
        script_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(script_dir, '..', 'config', 'tokens.json')) as f:
            return json.load(f)[env]
    except IOError:
        raise Exception("Missing config/tokens.json")
