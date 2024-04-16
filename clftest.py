import asyncio
import random
import time

async def worker(name, queue):
    while True:
        # Get a "work item" out of the queue.
        command = await queue.get()

        process = await asyncio.create_subprocess_shell(
            command,
            shell=True,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        print(f'[{name}] stdout: {stdout.decode().strip()}')

        # Notify the queue that the "work item" has been processed.
        queue.task_done()

async def main():
    # Create a queue that we will use to store our "workload".
    queue = asyncio.Queue(maxsize=50)

    # Generate commands to run and put them into the queue.
    total_sleep_time = 0
    for i in range(20):
        sleep_for = 2
        command = f'sleep {sleep_for}'
        queue.put_nowait(command)
        total_sleep_time += sleep_for


    # Create three worker tasks to process the queue concurrently.
    tasks = []
    for i in range(5):
        task = asyncio.create_task(worker(f'worker-{i}', queue))
        tasks.append(task)

    # Wait until the queue is fully processed.
    started_at = time.monotonic()
    await queue.join()
    total_slept_for = time.monotonic() - started_at

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)

    print('====')
    print(f'3 workers slept in parallel for {total_slept_for:.2f} seconds')
    print(f'total expected sleep time: {total_sleep_time:.2f} seconds')


asyncio.run(main())
