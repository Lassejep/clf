# sclf
Slow command line fuzzer

Fuzz a command with a list of arguments

options:
  -h, --help            show this help message and exit
  -e EXECUTE, --execute EXECUTE
                        The command to execute with FUZZ as the argument
                        placeholder
  -w WORDLIST, --wordlist WORDLIST
                        The wordlist to use as input to the command
  -c CONDITION, --condition CONDITION
                        The condition to check for in the output
  -i, --ignore-error    Ignore errors and continue fuzzing
  -s, --sanitize        Sanitize input to prevent ' " ` and \ characters from
                        breaking the command
