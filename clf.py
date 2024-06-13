#!/usr/bin/env python3
import codecs
import argparse
from multiprocessing import Process
import subprocess


def close():
    print('[-]Exiting...')
    exit(0)


def sanitize_input(input):
    input = input.replace('\\', '\\\\')
    input = input.replace('"', '\\"')
    input = input.replace("'", "\\'")
    input = input.replace('`', '\\`')
    return input


def build_command(command, wordlist, sanitize=False):
    line = 0
    with codecs.open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
        for word in f:
            if sanitize:
                word = sanitize_input(word)
            line += 1
            yield command.replace('FUZZ', f'"{word.strip()}"'), line


def count_lines(file):
    with codecs.open(file, 'r', encoding='utf-8', errors='ignore') as f:
        return sum(1 for _ in f)


def execute_command(
    command, line_count, condition, ignore_error
):
    command, current_line = command
    try:
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT)
        if condition is not None:
            print('\033[K', end='')
            print(f'[{current_line}/{line_count}]', end='\r')
            if condition in output.decode('utf-8'):
                print(f'\n[+]Condition met: {args.condition}')
                print(f'[+]Command: {command}')
                print(f'[+]Output: {output.decode("utf-8")}')
        else:
            print('\033[K', end='')
            print(f'[{current_line}/{line_count}]')
            print(f'[+]Command: {command}')
            print(f'[+]Output: {output.decode("utf-8")}')
    except subprocess.CalledProcessError as e:
        if not ignore_error:
            print('\033[K', end='')
            print(f'[{current_line}/{line_count}]')
            print(f'[-]Error: {e.output.decode("utf-8")}')
            close()
    except KeyboardInterrupt:
        close()


def fuzz_threaded(
    command, wordlist, condition=None, ignore_error=False,
    threads=4, sanitize=False
):
    print('[+]Loading wordlist...', end='\r')
    line_count = count_lines(wordlist)
    commands = build_command(command, wordlist, sanitize)
    while True:
        try:
            for _ in range(threads):
                p = Process(
                    target=execute_command,
                    args=(next(commands), line_count, condition, ignore_error)
                )
                p.start()
            p.join()
        except StopIteration:
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Fuzz a command with a list of arguments')
    parser.add_argument(
        '-e', '--execute', type=str, metavar='COMMAND',
        help='The command to execute with FUZZ as the argument placeholder'
    )
    parser.add_argument(
        '-w', '--wordlist', type=str, metavar='WORDLIST',
        help='The wordlist to use as input to the command'
    )
    parser.add_argument(
        '-c', '--condition', type=str, metavar='CONDITION',
        help='The condition to check for in the output'
    )
    parser.add_argument(
        '-i', '--ignore-error', action='store_true',
        help='Ignore errors and continue fuzzing'
    )
    parser.add_argument(
        '-s', '--sanitize', action='store_true',
        help='''Sanitize input to prevent \' \" ` and \\
        characters from breaking the command'''
    )
    parser.add_argument(
        '-t', '--threads', type=int, default=4,
        help='Number of threads to use for fuzzing'
    )
    args = parser.parse_args()

    if not args.execute or not args.wordlist:
        parser.print_help()
        exit(1)

    try:
        fuzz_threaded(
            args.execute, args.wordlist, args.condition,
            args.ignore_error, args.threads, args.sanitize
        )
    except KeyboardInterrupt:
        close()
