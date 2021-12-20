import sys
import threading


class Inspector:
    """Handles in and out data in pipe"""

    def __init__(self, bytes=False):
        self.bytes = bytes
        self._curr = None
        self.seq = 0
        self._state = {"prev": None, "curr": None}
        self.pipe_closed = True
        self.breaks = []

    def step(self):
        """Get next value from stdin"""
        try:
            if self.bytes:
                value = next(sys.stdin.buffer)
            else:
                value = next(sys.stdin)
            self.seq += 1
        except StopIteration:
            self.stdin_exhausted()
            return

        return value

    def _threaded_open(self, silence=True):
        """Consume stdin threaded"""
        from .shell import write_stdout, write_shell

        while True:
            self.prev = self._state["curr"]
            self.curr = self.step()

            if self.seq in self.breaks:
                self.close()
                write_shell(f"\nBreak at {self.seq}\n")
                break

            if self.pipe_closed:
                break

            if not silence:
                write_shell(self._state["curr"], bytes=self.bytes)

            write_stdout(self._state["curr"], bytes=self.bytes)

    def open(self, silence=True):
        """Open pipe"""
        self.pipe_closed = False
        self._thread = threading.Thread(target=self._threaded_open, args=(silence,))
        self._thread.start()

    def close(self):
        """Close pipe"""
        self.pipe_closed = True

    def flush(self):
        """Reset curr value and setting prev"""
        self._state["prev"] = self.curr
        self.curr = None

    def is_open(self):
        """Return true if pipe is open"""
        return not self.pipe_closed

    def is_closed(self):
        """Return true if pipe is closed"""
        return self.pipe_closed

    @property
    def curr(self):
        if self._state["curr"] is not None:
            return self._state["curr"]

        self._state["curr"] = self.step()
        return self._state["curr"]

    @curr.setter
    def curr(self, value):
        self._state["curr"] = value

    @property
    def prev(self):
        if self._state["prev"] is None:
            return b"" if self.bytes else ""
        return self._state["prev"]

    @prev.setter
    def prev(self, value):
        self._state["prev"] = value

    @property
    def state(self):
        return self._state

    def stdin_exhausted(self):
        from .shell import stdin_exhausted

        self.close()
        stdin_exhausted()
