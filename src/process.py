from queue import Queue
from threading import Thread

class Process:

    def __init__(self, p):
        self.endProcess = False # if the process is ended
        self.end = False # If the process is ended and there is no more reading
        self.p = p
        self.queue = Queue()
        self.thread = Thread(target=self.run)
        self.thread.start()
        self.length = 512
        self.stream = b''

    def readline(self):
        if(self.queue.empty()):
            return b''
        else:
            line = self.queue.get(block=False)
            
            if(self.queue.empty() and self.endProcess):
                self.end = True
                line += b'\x00' #Ending character string
            
            return line

    def readstream(self):
        self.stream = b''
        
        while(not self.queue.empty() and len(self.stream) < self.length):
            line = self.readline()
            self.stream += line
    
        return self.stream
        
    def run(self):

        out = 'undefined'
        
        while(self.p.poll() is None or out != b''):
            out = self.p.stdout.readline()
            self.queue.put(out)
            
        self.endProcess = True

    def kill(self):
        self.p.kill()

        
