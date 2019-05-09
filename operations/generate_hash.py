from optparse import OptionParser
import bcrypt

def execute(password, rounds):
    hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(rounds=rounds))
    print(hashed.decode())

def main():
    usage = "usage: %prog [options] password"
    parser = OptionParser(usage)
    parser.add_option("-n", "--number-rounds",
                      help="Number of rounds for bcrypt hash",
                      type="int", dest="rounds", default=14)

    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("You must provide a password")

    execute(args[0], options.rounds)

if __name__ == '__main__':
    main()
