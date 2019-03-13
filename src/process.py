from queue import Queue
from threading import Thread

"""
class Process
Wrapper of a subprocess to read the process output in non blocking mode
"""

class Process:

    def __init__(self, p):
        self.endProcess = False # if the process is ended
        self.end = False # If the process is ended and there is no more reading
        self.p = p
        self.queue = Queue() # Queue to store data
        self.thread = Thread(target=self.run) # Read continuously the output of the process
        self.thread.start()
        self.length = 512
        self.stream = b''

    """
    readline()
    Get the next element stored in the queue and return it
    """
        
    def readline(self):
        if(self.queue.empty()):
            return b''
        else:
            line = self.queue.get(block=False)
            
            if(self.queue.empty() and self.endProcess):
                self.end = True
                line += b'\x00' #Ending character string
            
            return line

    """
    readstream()
    read line until the buffer is full
    """
        
    def readstream(self):
        self.stream = b''
        
        while(not self.queue.empty() and len(self.stream) < self.length):
            line = self.readline()
            self.stream += line
    
        return self.stream

    """
    run
    read the process output while it is still active and store each line in a queue
    """
    def run(self):

        out = b'undefined'
        
        while(self.p.poll() is None or out != b''):
            out = self.p.stdout.readline()
            self.queue.put(out)
            
        self.endProcess = True


    """
    kill()
    kill the process
    """

    def kill(self):
        self.p.kill()

        
