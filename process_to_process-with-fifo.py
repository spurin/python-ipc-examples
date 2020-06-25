#!/usr/bin/env python3

import logging
import os
import time
from multiprocessing import Process

# Process1 logic
def process1():
    process1_logger = logging.getLogger('process1')
    process1_logger.info(f"Pid:{os.getpid()}")
    fifo = '/tmp/process_fifo.txt'

    # Create a fifo, os.mkfifo will block until there is a reader (process2)
    os.mkfifo(fifo)

    # Open fifo for writing
    file = open(fifo, 'w')

    # Write 10 entries
    for i in range(1,11):

        # Attempt to write to our fifo until succession
        while True:
            try:
                process1_logger.info(f"Writing {int(i)}")
                file.write(f"{i}\n")
                file.flush()
                break
            except:
                pass

    # Clean up fifo
    file.close()

    # Grace for the read process to complete
    process1_logger.info("Sleeping for 2")
    time.sleep(2)

    # Log completion
    process1_logger.info("Finished process 1")


# Process2 logic
def process2():
    process2_logger = logging.getLogger('process2')
    process2_logger.info(f"Pid:{os.getpid()}")
    fifo = '/tmp/process_fifo.txt'

    # Keep attempting to open the fifo, ignore race condition failures
    while True:
        try:
            file = open(fifo, 'r')
            break
        except:
            pass

    # Expect 10 entries
    count = 0
    while count < 10:
        while True:
            try:
                line = file.readline()
                process2_logger.info(f"Read: {int(line)}")
                count += 1
                break
            except:
                pass

    # Clean up fifo
    file.close()
    os.remove(fifo)

    # Log completion
    process2_logger.info("Finished process 2")


# Main
def main():

    # Setup parent logger and log pid
    parent_logger = logging.getLogger('parent')
    parent_logger.info(f"Pid:{os.getpid()}")

    # Setup processes
    procs = [Process(target=process1), Process(target=process2)]

    # Start processes
    for proc in procs:
        proc.start()

    # Run to completion
    for proc in procs:
        proc.join()

# Setup simple logging
logging.basicConfig(level=logging.INFO)

# Execute main
if __name__ == '__main__':
    main()
