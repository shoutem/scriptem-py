# ScriptEm

Collection of usefull scripts for ShoutEm platform

### Setup instructions
* Ensure you have `Xcode` installed
  * If not, install it via the App Store
* Ensure you have `brew` installed by running `brew --version`
  * If you get an error, perform the following 2 steps
  * Run `xcode-select --install`
  * Run `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
* Ensure that `python3` executable exists in your path and points to Python 3.7 or above by running `python3 --version`
  * If you get an error about missing `python3` command, run `brew install python3`
* Clone the repo into a local directory by runing `git clone https://github.com/shoutem/scriptem/`
  * If you get an error about missing `git` command, run `brew install git`
* Run `cd scriptem`
* Run `python3 -m pip install -r requirements.txt`
* Place the JSON document from [ScriptEm JIRA page](https://fiveminutes.jira.com/wiki/spaces/SE/pages/744816647/ScriptEm) into the `config/tokens.json`
* Do what you do best

### Usage

Scripts can have multiple options, to print them execute `python3 ./path/to/script.py -h`

If you want to save the output of a script to a file, you can use the `>` and `>>` commands. For example, `python3 ./users/get_app_users.py -h >> ~/Documents/app_users.csv`
* Using `>>` will replace a file if it exists, or create a new one if it doesn't and output all of the script output into it
* Using `>` create a new file if it doesn't exist or append the output to a file if it exists, this can be used to chain multiple scripts into one file
