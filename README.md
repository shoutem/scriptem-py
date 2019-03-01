# ScriptEm

Collection of usefull scripts for ShoutEm platform

### Setup instructions
* Ensure that `python3` executable exists in your path and points to Python 3.7 or above.
* Run `python3 -m pip install -r requirements.txt`
* Place the JSON document from [ScriptEm JIRA page](https://fiveminutes.jira.com/wiki/spaces/SE/pages/744816647/ScriptEm) into the `config/tokens.json`
* Do what you do best

### Usage

Scripts can have multiple options, to print them execute `python3 path/to/script.py -h`

If you want to save the output of a script to a file, you can use the `>` and `>>` commands. For example, `python3 users/get_app_users.py -h >> ~/Documents/app_users.csv`
* Using `>>` will replace a file if it exists, or create a new one if it doesn't and output all of the script output into it
* Using `>` create a new file if it doesn't exist or append the output to a file if it exists, this can be used to chain multiple scripts into one file
