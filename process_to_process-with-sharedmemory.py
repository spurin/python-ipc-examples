#!/usr/bin/env python3

import logging
import os
import time
from multiprocessing import Process, Array

# Process1 logic
def process1(shared):
    process1_logger = logging.getLogger('process1')
    process1_logger.info(f"Pid:{os.getpid()}")

    # Write 10 entries
    for i in range(1,11):

        # Attempt to write to our shared memory until succession
        while True:
            try:
                process1_logger.info(f"Writing {int(i)}")
                shared[i-1] = i
                if i % 6 == 0:
                    process1_logger.info("Intentionally sleeping for 5 seconds")
                    time.sleep(5)
                break
            except Exception as e:
                print(str(e))
                pass

    # Log completion
    process1_logger.info("Finished process 1")


# Process2 logic
def process2(shared):
    process2_logger = logging.getLogger('process2')
    process2_logger.info(f"Pid:{os.getpid()}")

    # Expect 10 entries
    for i in range(10):
        while True:
            try:
                line = shared[i]
                if line == -1:
                    process2_logger.info("Data not available sleeping for 1 second before retrying")
                    time.sleep(1)
                    raise Exception('pending')
                process2_logger.info(f"Read: {int(line)}")
                break
            except Exception:
                pass

    # Log completion
    process2_logger.info("Finished process 2")


# Main
def main():

    # Setup parent logger and log pid
    parent_logger = logging.getLogger('parent')
    parent_logger.info(f"Pid:{os.getpid()}")

    # Setup shared memory using Array (multiprocessing)
    arr = Array('i', [-1] * 10)

    # Setup processes
    procs = [Process(target=process1, args=(arr,)), Process(target=process2, args=(arr,))]

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
