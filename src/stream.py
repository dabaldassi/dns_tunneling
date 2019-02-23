import sys
import io
from threading import Thread
from queue import Queue

class Stream:
    def __init__(self):
        self.length=256
        self.buffer = b''
        self.thread = Thread(target=self.run)
        self.thread.start()
        self.queue = Queue()

    def read(self):
        # if(not self.queue.empty()):
        #     return self.queue.get(block=False)
        # return b'nothing'
        return self.queue.get(block=True)
    
    def run(self):
        input_stream = io.open(sys.stdin.fileno(), mode='rb') # Read stdin as binary
        print("Thread : Enter")
        while(True):
            r = input_stream.read(1) # Read one byte
            #print("Thread : ", r)
            self.buffer += r

            if(len(self.buffer) >= self.length):
               # print(256)
                self.queue.put(self.buffer)
                self.buffer = b''

    def stop(self):
        self.thread.kill()
