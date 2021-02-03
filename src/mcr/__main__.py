"""
Entrypoint module, in case you use `python -m mcr`.


Why does this file exist, and why __main__? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""

from mcr.cli import main
from mcr.cli import setup_logging

if __name__ == "__main__":
    setup_logging(name="mcr")
    main()
