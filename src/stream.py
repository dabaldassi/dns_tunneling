import sys
import os
from threading import Thread
from queue import Queue

class Stream:
    def __init__(self):
        self.length=100
        self.buffer = b''
        self.queue = Queue()
        self.thread = Thread(target=self.run)
        self.thread.start()
      

    def read(self):
        if(not self.queue.empty()):
            return self.queue.get(block=False)
        return b'nothing'
        
    def run(self):
        
        while(True):
            r = os.read(sys.stdin.fileno(), 1024)
            #print(r)
            self.queue.put(r)
           
    def stop(self):
        self.thread.kill()
