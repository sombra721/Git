#!/usr/bin/python
import time

class TimeTick:
    """
    Represent a time stamps and elapsed time
    Attributes:
        start_t
        stop_t
        elapse_t
    """
    def __init__(self):
        self.start_t  = 0.0
        self.stop_t   = 0.0
        self.elapse_t = 0.0

    def __str__(self):
        return str(self.elapse_t)

    def start(self):
        self.start_t = time.time()
        return self.start_t

    def stop (self):
        self.stop_t = time.time()
        self.elapse_t = self.stop_t - self.start_t
        return self.stop_t

    def getElapseTime(self):                
        return self.elapse_t


