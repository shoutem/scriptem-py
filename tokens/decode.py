# import os
from optparse import OptionParser
import base64
import json
import zlib


def decompress(obj, new_obj={}):
    for k, v in obj.items():
        if isinstance(v, dict):
            if "ct" in v and "v" in v:
                zipped_bytes = base64.b64decode(v["v"])
                
                if v["ct"] == "gzip":
                    decompressed_content = zlib.decompress(zipped_bytes, zlib.MAX_WBITS|32)
                else:
                    print("Unkown compression format")
                    exit(1)
                
                new_obj[k] = json.loads(decompressed_content)
            else:
                new_obj[k] = decompress(v, {})
        else:
            new_obj[k] = v

    return new_obj


def execute(token):
    parts = token.split(".")

    if len(parts) != 3:
        print("Token should be in format [JWT_header].[JWT_body].[signature]")
        exit(0)

    for part in parts[:2]: # signature part of JWT is not Base64
        # JWT does not add padding to tokens, so we add it back becase 'b64decode' will complain
        decoded = base64.b64decode(part + '=' * (-len(part) % 4))
        parsed = json.loads(decoded)

        decompressed = decompress(parsed)

        print(json.dumps(decompressed, indent=4))


def main():
    usage = "usage: %prog token"
    parser = OptionParser(usage)

    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("You must provide token to decode")

    execute(args[0])


if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from shared import network, auth, config, prompt, errors
    main()
