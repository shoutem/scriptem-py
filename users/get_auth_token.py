from optparse import OptionParser
import base64
import json
import re

def execute(username, password, realm, decode, env):
    accessJwt = auth.get_user_token(username, password, env, realm)

    tokens.decode(accessJwt) if decode else print(accessJwt)


def main():
    usage = "usage: %prog [options] username password"
    parser = OptionParser(usage)
    
    parser.add_option("-d", "--decode",
                      help="Decode from base64 before printing",
                      action="store_true", dest="decode", default=False)
    parser.add_option("-r", "--realm",
                      help="ID of realm (application) for which to get the token, default is builder (0)",
                      dest="realm", default=0)
    parser.add_option("-e", "--env",
                      help="Environment to run this script on, default: 'qa', options are 'prod', 'qa', 'dev', 'local'",
                      type="string", dest="env", default="qa")
    
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("You must provide username and password")
    if options.env not in ['prod', 'qa', 'dev', 'local']:
        parser.error("Incorrect environment {}".format(options.env))

    execute(args[0], args[1], options.realm, options.decode, options.env)


if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from shared import network, auth, config
    import tokens
    main()
