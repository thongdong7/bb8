import sys
from os.path import dirname, exists, abspath
from subprocess import Popen

import click
import yaml

from bb8.script.config import default_config_file
from bb8.script.utils import exit_msg


@click.command('up', help='Run service')
@click.option('--config', '-c', 'config_file', default=default_config_file, help='Path to config file')
def cmd_up(config_file):
    if not exists(config_file):
        exit_msg('Invalid config file: %s' % config_file)

    data = yaml.load(open(config_file))
    # print(data)

    cmds = data.get('up', [])
    if not cmds:
        print('There is no commands to execute')
        sys.exit(1)

    cwd = dirname(abspath(config_file))
    # print(cwd)

    processes = []

    for cmd in cmds:
        try:
            p = Popen(cmd, shell=True, cwd=cwd)
            # , stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            processes.append(p)
        except Exception as e:
            print('Error when execute command: %s' % cmd)
            print(str(e))
            close_processes(processes)

    for p in processes:
        p.wait()

    print('Complete')


def close_processes(processes):
    for p in processes:
        try:
            p.terminate()
        except:
            p.kill()
