import sys

import click


def error_msg(msg):
    click.echo(click.style(msg, fg='red'))


def exit_msg(msg):
    error_msg(msg)
    sys.exit(1)


def write_msg(msg):
    click.echo(click.style(msg, dim=True))
