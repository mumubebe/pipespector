import cmd
import argparse
import os
import sys
from .inspector import Inspector


outshell = open("/dev/tty", "w")
inshell = open("/dev/tty")


class PipeShell(cmd.Cmd):
    intro = "Type 'help' or '?' to list commands \n"
    use_rawinput = 0
    name = "pipespector"

    def __init__(self, name=None, *args, **kwargs):
        super().__init__(stdout=outshell, stdin=inshell, *args, **kwargs)

        self.inspector = Inspector()

        if name:
            self.name = name

        self.prompt = f"({self.name})> "

    def do_exit(self, arg):
        """Exit program"""
        return True

    def do_curr(self, arg):
        """Print the current value to shell"""
        if self.inspector.curr is None:
            write_shell("No current value in available\n")
        else:
            write_shell(self.inspector.curr, bytes=True)

    def do_prev(self, arg):
        """Print the previous value to shell"""
        if self.inspector.prev is None:
            write_shell("No previous value in available\n")
        else:
            write_shell(self.inspector.prev, bytes=True)

    def do_info(self, arg):
        """Print current pipe information"""
        write_shell(
            f"{os.readlink('/proc/%d/fd/0' % os.getpid())} -> {self.name} -> {os.readlink('/proc/%d/fd/1' % os.getpid())}\n",
            self.outshell,
        )
        write_shell(f"({self.inspector.seq}) values has been passed in pipe \n")
        write_shell("Current value in pipe: ")
        write_shell(self.inspector.curr, bytes=True)
        write_shell("Previous value in pipe: ")
        write_shell(self.inspector.prev, bytes=True)

    def do_next(self, arg):
        """Pass the current value to stdout"""
        curr = self.inspector.curr
        if curr:
            write_shell("stdout: \n")
            write_shell(curr, bytes=True)
            write_stdout(curr)
            self.inspector.flush()
        else:
            write_shell("No current value in pipe\n")

    def do_exec(self, arg):
        """
        Execute python script. This function works mainly to modify any future output.
        it's possible to modify both curr and prev. Note that all variables in pipe are byte objects.

        Example 1: curr = b'{"json": "object"}' # Set a string to curr value
        Example 2: curr = prev + b"\n" # Set curr value as previous value with a line break
        """
        try:
            exec(arg, globals(), self.inspector.state)
        except Exception as e:
            write_shell(str(e))


def write_shell(data, bytes=False):
    """Print value to current shell"""
    if bytes:
        outshell.buffer.write(data)
    else:
        outshell.write(data)
    outshell.flush()


def write_stdout(data):
    """Pass data to stdout. This will not be printed in shell"""
    sys.stdout.buffer.write(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name")
    parser.add_argument("-b", "--byte")
    args = parser.parse_args()

    PipeShell(args.name).cmdloop()
