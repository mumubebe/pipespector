from .shell import main
import os

if not os.isatty(0):
    main()

