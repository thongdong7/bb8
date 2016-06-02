import sys

import click


def exit_msg(msg):
    print(msg)
    sys.exit(1)


def write_msg(msg):
    print(msg)


def error_msg(msg):
    click.echo(click.style(msg, fg='yellow'))
