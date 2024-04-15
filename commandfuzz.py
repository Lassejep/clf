#!/usr/bin/env python3

import os
import subprocess
from sys import argv
import argparse
import codecs

def run_command(command, condition=None):
    try:
        out = subprocess.check_output(command, shell=True)
        if condition is not None:
            if condition in out.decode('utf-8'):
                return f'Command: {command}' + f'Output: {out.decode("utf-8")}'
        else:
            return f'Command: {command}' + f'Output: {out.decode("utf-8")}'
    except subprocess.CalledProcessError as e:
        raise e

def build_command(command, wordlist):
    with codecs.open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
        for word in f:
            if args.sanitize:
                word = sanitize_input(word)
            yield command.replace('FUZZ', f'"{word.strip()}"')

def count_lines(file):
    with codecs.open(file, 'r', encoding='utf-8', errors='ignore') as f:
        return sum(1 for _ in f)

def sanitize_input(input):
    input = input.replace('\\', '\\\\')
    input = input.replace('"', '\\"')
    input = input.replace("'", "\\'")
    input = input.replace('`', '\\`')
    return input


def main():
    commands = build_command(args.execute, args.wordlist)
    print('loading wordlist...', end='\r')
    count = count_lines(args.wordlist)
    print(' '*20, end='\r')
    current = 0
    for command in commands:
        current += 1
        print(f'[{current}/{count}]', end='\r')
        try:
            out = run_command(command, args.condition)
            if out is not None:
                print(out)
        except subprocess.CalledProcessError as e:
            if not args.ignore_error:
                print(f'[{current}/{count}]')
                print(f'Command: {command}')
                print(f'Error: {e}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fuzz a command with a list of arguments')
    parser.add_argument('-e', '--execute', type=str, help='The command to execute with FUZZ as the argument placeholder')
    parser.add_argument('-w', '--wordlist', type=str, help='The wordlist to use as input to the command')
    parser.add_argument('-c', '--condition', type=str, help='The condition to check for in the output')
    parser.add_argument('-i', '--ignore-error', action='store_true', help='Ignore errors and continue fuzzing')
    parser.add_argument('-s', '--sanitize', action='store_true', help='Sanitize input to prevent \' \" \` and \\ characters from breaking the command')
    args = parser.parse_args()

    if not args.execute or not args.wordlist:
        parser.print_help()
        exit(1)

    main()
