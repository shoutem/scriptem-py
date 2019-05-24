from optparse import OptionParser
import bcrypt

def execute(password):
    hashed_password = input("Hashed password: ")
    isValid = bcrypt.checkpw(password.encode('utf8'), hashed_password.encode('utf8'))
    print(isValid)

def main():
    usage = "usage: %prog [options] password"
    parser = OptionParser(usage)

    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("You must provide a password")

    execute(args[0])

if __name__ == '__main__':
    main()
