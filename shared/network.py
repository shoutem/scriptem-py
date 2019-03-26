import requests

base_get_headers = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/x-www-form-urlencoded"
}

base_post_headers = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json"
}

def get(uri, opts={}):
    headers = opts.get("headers", {})
    headers.update(base_get_headers)
    query = opts.get("query", {})
    
    return requests.get(uri, headers=headers, params=query)


def patch(uri, opts={}):
    headers = opts.get("headers", {})
    headers.update(base_post_headers)
    body = opts.get("body", {})

    return requests.patch(uri, headers=headers, json=body)


def post(uri, opts={}):
    headers = opts.get("headers", {})
    headers.update(base_post_headers)
    body = opts.get("body", {})

    return requests.post(uri, headers=headers, json=body)
