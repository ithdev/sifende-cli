#!/usr/bin/env python3
"""Direct entry point: `python sifende.py <command> ...`."""

import sys

from sifende.cli import main

if __name__ == "__main__":
    sys.exit(main())
