#!/usr/bin/env python3

import codecs
import argparse
import asyncio

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
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return stdout, stderr

async def worker(queue):
    clear = '\033[K'
    total = count_lines(args.wordlist)
    count = 0
    while True:
        command = await queue.get()
        count += 1
        print(f'{clear}[{count}/{total}] {command}', end='\r')

        stdout, stderr = await run_command(command)
        if args.condition:
            if args.condition in stdout.decode('utf-8'):
                print(f'\n[+] Condition met: {args.condition}')
                print(f'[+] Command: {command}')
                print(f'[+] Output: {stdout.decode("utf-8")}')
        else:
            print(f'\n[+] Command: {command}')
            print(f'[+] Output: {stdout.decode("utf-8")}')

        if not args.ignore_error and stderr:
            print(f'\n[-] Error: {stderr.decode("utf-8")}')
        queue.task_done()

async def main():
    clear = '\033[K'
    commands = build_command(args.execute, args.wordlist)
    print('loading wordlist...', end='\r')
    total = count_lines(args.wordlist)
    queue = asyncio.Queue(maxsize=args.threads)
    for i, command in enumerate(commands, 1):
        await queue.put(command)
    print(f'{clear}', end='\r')

    tasks = []
    for _ in range(args.threads):
        task = asyncio.create_task(worker(queue))
        tasks.append(task)
    await queue.join()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fuzz a command with a list of arguments')
    parser.add_argument('-e', '--execute', type=str, help='The command to execute with FUZZ as the argument placeholder')
    parser.add_argument('-w', '--wordlist', type=str, help='The wordlist to use as input to the command')
    parser.add_argument('-c', '--condition', type=str, help='The condition to check for in the output')
    parser.add_argument('-i', '--ignore-error', action='store_true', help='Ignore errors and continue fuzzing')
    parser.add_argument('-s', '--sanitize', action='store_true', help='Sanitize input to prevent \' \" ` and \\ characters from breaking the command')
    parser.add_argument('-t', '--threads', type=int, default=4, help='Number of threads to use for fuzzing')
    args = parser.parse_args()

    if not args.execute or not args.wordlist:
        parser.print_help()
        exit(1)

    asyncio.run(main())
