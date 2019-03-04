import requests

base_headers = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json"
}

def get(uri, opts={}):
    headers = opts.get("headers", {})
    headers.update(base_headers)
    query = opts.get("query", {})
    
    return requests.get(uri, headers=headers, params=query)

def post(uri, opts={}):
    headers = opts.get("headers", {})
    headers.update(base_headers)
    body = opts.get("body", {})

    return requests.post(uri, headers=headers, json=body)