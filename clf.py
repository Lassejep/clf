#!/usr/bin/env python3
import codecs
import argparse
import asyncio


def close():
    print('[-]Exiting...')
    exit(0)


def sanitize_input(input):
    input = input.replace('\\', '\\\\')
    input = input.replace('"', '\\"')
    input = input.replace("'", "\\'")
    input = input.replace('`', '\\`')
    return input


def build_command(command, wordlist):
    with codecs.open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
        for word in f:
            if args.sanitize:
                word = sanitize_input(word)
            yield command.replace('FUZZ', f'"{word.strip()}"')


def count_lines(file):
    with codecs.open(file, 'r', encoding='utf-8', errors='ignore') as f:
        return sum(1 for _ in f)


async def run_command(command):
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout, stderr


async def queue_worker(queue):
    while True:
        command = await queue.get()
        stdout, stderr = await run_command(command)
        if args.condition:
            if args.condition in stdout.decode():
                print(f'[+]Command: {command}')
                print(f'[+]Condition met: {args.condition}')
                print(f'[+]Output: {stdout.decode()}')
        else:
            print(f'[+]Command: {command}')
            print(f'[+]Output: {stdout.decode()}')
        if not args.ignore_error:
            if stderr:
                print(f'[-]Error: {stderr.decode()}')
        queue.task_done()


async def run():
    print('Loading wordlist...')
    total_lines = count_lines(args.wordlist)
    completed_lines = 0
    tasks = []
    command_generator = build_command(args.execute, args.wordlist)
    queue = asyncio.Queue(maxsize=args.threads)
    task = None
    for command in command_generator:
        completed_lines += 1
        if queue.full():
            await queue.join()
            await queue.put(command)
            tasks.append(task)
        else:
            await queue.put(command)
            task = asyncio.create_task(queue_worker(queue))
        print(f'[{completed_lines}/{total_lines}]', end='\r')

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
        asyncio.run(run())
    except KeyboardInterrupt:
        close()
