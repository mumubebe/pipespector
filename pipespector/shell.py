import cmd
import argparse
import os
import sys
import signal
from .inspector import Inspector


outshell = open("/dev/tty", "w")
inshell = open("/dev/tty")


class PipeShell(cmd.Cmd):
    intro = "Type 'help' or '?' to list commands \n"
    use_rawinput = 0
    name = "pipespector"

    def __init__(self, bytes=False, name=None, open=False, *args, **kwargs):
        super().__init__(stdout=outshell, stdin=inshell, *args, **kwargs)

        self.inspector = Inspector(bytes=bytes)
        self.bytes = bytes

        if name:
            self.name = name

        self.prompt = f"({self.name})> "

        if open:
            self.inspector.open()

    def do_exit(self, arg):
        """Exit program"""
        return True

    def do_break(self, arg):
        """Break at any glob pattern"""
        if arg == "clear":
            self.inspector.break_patterns = []
        else:
            self.inspector.break_patterns.append(arg)

    def do_seq(self, arg):
        """Print sequence number"""
        write_shell(str(self.inspector.seq))

    def do_curr(self, arg):
        """Print the current value to shell"""
        if self.inspector.curr is None:
            write_shell("No current value in available\n")
        else:
            write_shell(self.inspector.curr, bytes=self.bytes)

    def do_close(self, arg):
        """Close pipe. This will pause the flow"""
        if self.inspector.is_open():
            self.inspector.close()
        else:
            write_shell("Pipe is not open\n")

    def do_open(self, arg):
        """Open up pipe and let it flow freely"""
        if self.inspector.is_closed():
            self.inspector.open(silence=True)
        else:
            write_shell("Pipe is already open\n")

    def do_prev(self, arg):
        """Print the previous value to shell"""
        if self.inspector.prev is None:
            write_shell("No previous value in available\n")
        else:
            write_shell(self.inspector.prev, bytes=True)

    def do_info(self, arg):
        """Print current pipe information"""
        write_shell(
            f"{os.readlink('/proc/%d/fd/0' % os.getpid())} -> {self.name} -> {os.readlink('/proc/%d/fd/1' % os.getpid())}\n"
        )
        write_shell(f"({self.inspector.seq}) values has been passed in pipe \n")
        write_shell("Current value in pipe: ")
        write_shell(self.inspector.curr, bytes=self.bytes)
        write_shell("Previous value in pipe: ")
        write_shell(self.inspector.prev, bytes=self.bytes)

    def do_step(self, arg):
        """Step one value"""
        if self.inspector.is_closed():
            curr = self.inspector.curr
            if curr:
                write_shell("stdout: \n")
                write_shell(curr, bytes=self.bytes)
                write_stdout(curr)
                self.inspector.flush()
            else:
                write_shell("No current value in pipe\n")
        else:
            write_shell("Cannot step, pipe is open\n")

    def do_exec(self, arg):
        """
        Execute python script. This function works mainly to modify any future output.
        it's possible to modify both curr and prev. Note that all variables in pipe are byte objects.

        Example 1: curr = b'{"json": "object"}' # Set a string to curr value
        Example 2: curr = prev + b"\n" # Set curr value as previous value with a line break
        """
        if self.inspector.is_closed():
            try:
                exec(arg, globals(), self.inspector.state)
            except Exception as e:
                write_shell(str(e))
        else:
            write_shell("Cannot execute script while pipe is open\n")


def stdin_exhausted():
    write_shell("No more items left -- exiting program...\n")

    outshell.flush()
    sys.stdout.flush()

    # TODO:  this method is called from a thread (not main)
    # sys.exit() only raises SystemExit inside that thread, ie closing it
    os._exit(0) #note the underscore


def write_shell(data, bytes=False):
    """Print value to current shell"""
    if bytes:
        outshell.buffer.write(data)
    else:
        outshell.write(data)
    outshell.flush()


def write_stdout(data, bytes=False):
    """Pass data to stdout. This will not be printed in shell"""
    if bytes:
        sys.stdout.buffer.write(data)
    else:
        sys.stdout.write(data)
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name")
    parser.add_argument("-b", "--bytes", dest="bytes", action="store_true", help="")
    parser.add_argument(
        "-o", "--open", dest="open", action="store_true", help="Start with open pipe"
    )
    args = parser.parse_args()

    PipeShell(bytes=args.bytes, name=args.name, open=args.open).cmdloop()
