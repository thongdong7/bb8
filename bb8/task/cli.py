from genericpath import exists
from os import chdir
from os.path import abspath, dirname

import click
import yaml

from bb8.script.config import default_config_file
from bb8.script.utils import exit_msg
from bb8.task.manager import TaskManager


@click.command('task', help='Run tasks')
@click.argument('task_name')
@click.option('--config', '-c', 'config_file', default=default_config_file, help='Path to config file')
def cli_run_task(config_file, task_name):
    if not exists(config_file):
        exit_msg('Invalid config file %s' % config_file)

    config_file = abspath(config_file)
    chdir(dirname(config_file))

    data = yaml.load(open(config_file))
    tasks = data.get('task', {})
    if not tasks:
        exit_msg("There is no task")

    if task_name not in tasks:
        exit_msg("No task '{0}".format(task_name))

    task_manager = TaskManager(tasks)
    task_manager.execute(task_name)
