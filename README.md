# clf
Command Line Fuzzer

Fuzz a command with a wordlist and check for a condition in the output.

| Command | Description |
| ------- | ----------- |
| -h, --help | Show help message and exit |
| -e COMMAND, --execute COMMAND | The command to execute with FUZZ as the argument placeholder |
| -w WORDLIST, --wordlist WORDLIST | The wordlist to use as input to the command |
| -c CONDITION, --condition CONDITION | The condition to check for in the output |
| -i, --ignore-error | Ignore errors and continue fuzzing |
| -s, --sanitize | Sanitize input to prevent ' " ` and \ characters from breaking the command |
| -t THREADS, --threads THREADS | The number of threads to use for fuzzing |

## Examples
```bash
python clf.py -e "echo FUZZ" -w wordlist.txt 
```
