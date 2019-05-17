#!/usr/bin/env python3
from sys import stderr


def print_error_message(*args):
    print(*args, file=stderr)
    exit(1)
