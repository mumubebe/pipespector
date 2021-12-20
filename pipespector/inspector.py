import sys

class Inspector:
    """Handles in and out data in pipe"""

    def __init__(self):
        self._curr = None
        self.seq = 0
        self._state = {"prev": None, "curr": None}

    def _next(self):
        """Get next value from stdin"""
        try:
            value = next(sys.stdin.buffer)
            self.seq += 1
        except StopIteration:
            self._exit_program()

        return value

    def flush(self):
        """Reset curr value and setting prev"""
        self._state["prev"] = self.curr
        self.curr = None

    @property
    def curr(self):
        if self._state["curr"] is not None:
            return self._state["curr"]

        self._state["curr"] = self._next()
        return self._state["curr"]

    @curr.setter
    def curr(self, value):
        self._state["curr"] = value

    @property
    def prev(self):
        if self._state["prev"] is None:
            return b""
        return self._state["prev"]

    @property
    def state(self):
        return self._state

    def _exit_program(self):
        from .shell import write_shell
        write_shell("No more items left -- exiting program...\n")
        sys.exit()
