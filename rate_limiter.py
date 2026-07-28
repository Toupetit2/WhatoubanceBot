import requests
import os
import time
import threading


class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            now = time.time()
            self.calls = [c for c in self.calls if now - c < self.period]
            if len(self.calls) >= self.max_calls:
                wait = self.period - (now - self.calls[0])
                if wait > 0:
                    time.sleep(wait)
            self.calls.append(time.time())
