import os
from os.path import exists, dirname, join
from time import time, ctime

import click as click
import yaml
from dateutil.parser import parse

from bb8.container import bb8, git_push, data_folder
from bb8.monitor import FileMonitor, FileMonitorPool
from bb8.utils.io_utils import copy_file, is_diff, show_diff

config_file = 'bb8.yml'

paths = []


def load_paths():
    global paths

    config = yaml.load(open(config_file))
    paths = config['paths']


@click.command('sync', help='Copy change files and push to git')
def sync_files():
    # Init monitor
    def sync_and_push(path=None):
        start = time()

        with click.progressbar(length=2,
                               label='Copy files and push to git') as bar:

            change = bb8.sync_paths(paths)
            bar.update(1)

            if change:
                git_push.commit_and_push()
                bar.update(2)

            if change:
                print('\nSynced in %s seconds' % (time() - start))
            else:
                print('\nSync: no change')

    # monitor paths
    paths_monitor = FileMonitor(sync_and_push)

    def on_config_change(path=None):
        print('config change')

        # Reload paths
        load_paths()

        # Update watch files
        paths_monitor.watch_multiple(bb8.get_monitor_files(paths))

        # Trigger sync and push
        sync_and_push()

    # Reload paths
    load_paths()

    # Update watch files
    paths_monitor.watch_multiple(bb8.get_monitor_files(paths))

    # Monitor config_file
    config_monitor = FileMonitor(on_config_change)
    config_monitor.watch(config_file)

    file_monitor_pool = FileMonitorPool()
    file_monitor_pool.add_file_monitor(config_monitor)
    file_monitor_pool.add_file_monitor(paths_monitor)

    print("Wait for file change")
    file_monitor_pool.start()


@click.command('restore', help='Restore config files from git')
def restore_files():
    load_paths()

    for path in paths:
        remote_path = join(data_folder, path)
        local_path = bb8.template_engine.render(path)
        # print("Replace file {0} by {1}".format(compiled_path, path))

        if not exists(local_path):
            print("Create file %s" % local_path)
            copy_file(remote_path, local_path)
        elif not exists(remote_path):
            print("Create file %s" % remote_path)
            copy_file(local_path, remote_path)
        else:
            if not is_diff(local_path, remote_path):
                continue

            local_time = parse(ctime(os.path.getmtime(local_path)))
            remote_time = parse(ctime(os.path.getmtime(remote_path)))

            if remote_time > local_time:
                print("Override remote to local: {0}".format(remote_path))
                show_diff(local_path, remote_path)

                copy_file(remote_path, local_path)
            else:
                print("Local is newer, need to sync: {0}".format(remote_path))
                show_diff(local_path, remote_path)

                copy_file(local_path, remote_path)

            print("-----------------")
