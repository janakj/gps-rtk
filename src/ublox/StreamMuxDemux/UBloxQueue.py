import time
from queue import Queue
from threading import Thread

class UBloxQueue():
    def __init__(self, ttl, timeout):
        self._q = Queue()
        self._max_ttl = ttl
        self._timeout = timeout

        self._watcher_thread = Thread(target=self._watch_old_items)
        self._watcher_thread.daemon = True
        self._watcher_thread.start()
    
    def _watch_old_items(self):
        while True:
            ttl = self._discard_old_items()
            time.sleep(ttl)

    def _discard_old_items(self):
        now = time.time()
        while self._q.qsize() > 0:
            item, expires_at = self._q.queue[-1]
            if expires_at <= now:
                self._q.get()
            else:
                ttl = expires_at - now
                return ttl
        return self._max_ttl

    def put(self, item):
        expires_at = time.time() + self._max_ttl
        self._q.put((item, expires_at))

    def get(self):
        get_at = time.time()
        try:
            item, expires_at = self._q.get(True, self._timeout)
            while expires_at <= get_at:
                item, expires_at = self._q.get(True, self._timeout)
            return item
        except:
            return b''
