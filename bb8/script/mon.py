import click as click
from bb8.monitor import MonAndRun
from bb8.script.config import default_config_file


@click.command('mon', help='Monitor files and run commands when change')
@click.option('--config', '-c', 'config_file', default=default_config_file, help='Path to config file')
def mon_and_run(config_file):
    mon = MonAndRun(config_file)
    mon.start()
