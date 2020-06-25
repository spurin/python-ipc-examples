#!/usr/bin/env python3

import logging
import os
import time
from multiprocessing import Process, Array
# On MacPro 5,1, module gave Illegal instruction: 4
# Installing non-wheel version with non-wheel dependencies
# in clean venv works
#
# pip install zerorpc --no-binary :all:
import zerorpc

# Process1 logic
def process1():
    process1_logger = logging.getLogger('process1')
    process1_logger.info(f"Pid:{os.getpid()}")

    class RPC(object):
        def __init__(self):
            self.value = 0

        def get_item(self):
            self.value += 1
            process1_logger.info(f"Writing {self.value}")
            return self.value

    # Setup an RPC Server
    s = zerorpc.Server(RPC())
    s.bind("tcp://0.0.0.0:4242")

    # Run the server without background'ing for 5 seconds
    # (s.run() will block)
    zerorpc.gevent.spawn(s.run)
    zerorpc.gevent.sleep(5)

    # Log completion
    process1_logger.info("Finished process 1")


# Process2 logic
def process2():
    process2_logger = logging.getLogger('process2')
    process2_logger.info(f"Pid:{os.getpid()}")

    c = zerorpc.Client()
    c.connect("tcp://127.0.0.1:4242")

    # Expect 10 entries
    for i in range(10):
        while True:
            try:
                line = c.get_item()
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
