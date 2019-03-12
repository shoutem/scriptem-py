from optparse import OptionParser
import base64
import json

def execute(username, password, decode, env):
    token = auth.get_user_token(username, password, env)

    if decode:
        for part in map(base64.b64decode, token.split(".")[:2]): # signature part of JWT is not Base64
            parsed = json.loads(part.decode('utf-8'))
            print(json.dumps(parsed, indent=4))
    else:
        print(token)


def main():
    usage = "usage: %prog [options] username password"
    parser = OptionParser(usage)
    
    parser.add_option("-d", "--decode",
                      help="Decode from base64 before printing",
                      action="store_true", dest="decode", default=False)
    parser.add_option("-e", "--env",
                      help="Environment to run this script on, default: 'qa', options are 'prod', 'qa', 'dev'",
                      type="string", dest="env", default="qa")
    
    (options, args) = parser.parse_args()
    
    if len(args) != 2:
        parser.error("You must provide username and password")
    if options.env not in ['prod', 'qa', 'dev']:
        parser.error("Incorrect environment {}".format(options.env))

    execute(args[0], args[1], options.decode, options.env)


if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from shared import network, auth, config
    main()
