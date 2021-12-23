import sys
import threading
import fnmatch


class Inspector:
    """Handles in and out data in pipe"""

    def __init__(self, bytes=False):
        self.bytes = bytes
        self._curr = None
        self.seq = 0
        self._state = {"prev": None, "curr": None}
        self.pipe_closed = True
        self.break_patterns = []

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

    def _threaded_open(self):
        """Consume stdin threaded"""
        from .shell import write_stdout, write_shell

        if self.curr is None:
            self.curr = self.step()
        else:
            # Pass any values to stdout thats already in pipe.
            # This is because pattern matching etc should not be triggered by values already
            # inside the pipe - only values passing from stdin -> pipespector
            write_stdout(self.curr, bytes=self.bytes)
            self.prev = self._state["curr"]
            self.curr = self.step()

        while True:
            if self.pattern_match(self.curr, self.break_patterns):
                self.close()
                write_shell(f"\nPattern found - pipe closed at ({self.seq})\n")
                break

            if self.pipe_closed:
                break

            write_stdout(self.curr, bytes=self.bytes)

            self.prev = self._state["curr"]
            self.curr = self.step()

    def open(self):
        """Open pipe"""
        self.pipe_closed = False
        self._thread = threading.Thread(target=self._threaded_open)
        self._thread.start()

    def pattern_match(self, value, patterns):
        """Return true if any match"""
        for p in patterns:
            if fnmatch.fnmatch(value.strip(), p):
                return True
        return False

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
        return self._state["curr"]

    @curr.setter
    def curr(self, value):
        self._state["curr"] = value

    @property
    def prev(self):
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
