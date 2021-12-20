from .shell import main
import os

if not os.isatty(0) and not os.isatty(1):
    main()
else:
    raise Exception(
        "Pipespector cannot be connected to file descriptors that are tty-like devices"
    )
