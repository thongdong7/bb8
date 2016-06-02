from bb8.process.exception import CommandError
from bb8.script.utils import error_msg
from os import chdir
from time import time

import os
import yaml
from os.path import abspath, curdir, dirname

from tornado.ioloop import IOLoop, PeriodicCallback

from bb8.process.cmd import run_cmd


class FileChange(Exception):
    def __init__(self, path, *args, **kwargs):
        super(FileChange).__init__(*args, **kwargs)
        self.path = path


class FileMonitor:
    def __init__(self, callback):
        self.callback = callback
        self.watched_files = set()
        self.modify_times = {}

    def watch(self, path):
        self.watched_files.add(path)

    def watch_multiple(self, paths):
        for path in paths:
            self.watched_files.add(path)

    def scan(self):
        try:
            for path in self.watched_files:
                self.check_file(path)
        except FileChange as e:
            self.callback(e.path)

    def check_file(self, path):
        try:
            modified = os.stat(path).st_mtime
        except Exception:
            return

        if path not in self.modify_times:
            self.modify_times[path] = modified
            return
        if self.modify_times[path] != modified:
            self.modify_times[path] = modified

            raise FileChange(path)


class FileMonitorPool:
    def __init__(self):
        self.io_loop = IOLoop.instance()
        self.file_monitors = []

    def add_file_monitor(self, file_monitor):
        self.file_monitors.append(file_monitor)

    def start(self, check_time=500):
        scheduler = PeriodicCallback(self._callback, check_time, io_loop=self.io_loop)
        scheduler.start()

        self.io_loop.start()

    def _callback(self):
        for file_monitor in self.file_monitors:
            file_monitor.scan()


class MonAndRun(object):
    def __init__(self, gen_file):
        self.gen_file = abspath(gen_file)
        self.path_maps = {}

        self.paths_monitor = FileMonitor(self.path_change)

        self.config_monitor = FileMonitor(self.on_config_change)
        self.config_monitor.watch(self.gen_file)

        self.file_monitor_pool = FileMonitorPool()
        self.file_monitor_pool.add_file_monitor(self.config_monitor)
        self.file_monitor_pool.add_file_monitor(self.paths_monitor)

    def load_path_map(self, path=None):
        data = yaml.load(open(self.gen_file).read())
        gen_items = data['mon']

        ret_path_maps = {}
        for item in gen_items:
            # print(item)
            for path in item['paths']:
                ret_path_maps[path] = item['cmds']

        self.path_maps = ret_path_maps

        self.paths_monitor.watch_multiple(self.path_maps.keys())

    def path_change(self, path=None):
        start = time()

        if path not in self.path_maps:
            print('Could not found commands for %s' % path)
            return

        # print(self.path_maps[path])
        try:
            cmds = self.path_maps[path]
            for cmd in cmds:
                output = run_cmd(cmd)
                print(output)
        except CommandError as e:
            error_msg(str(e))

        print('\nCompleted in %s seconds' % (time() - start))

    def on_config_change(self, path=None):
        print('config change')
        self.load_path_map(self.gen_file)

    def start(self):
        # gen_file = 'gen.yml'
        # gen_file = '/data/projects/coffee/gen.yml'

        current_folder = abspath(curdir)

        try:
            gen_dir = dirname(self.gen_file)
            chdir(gen_dir)

            self.load_path_map()

            print("Wait for file change")
            self.file_monitor_pool.start()
        finally:
            chdir(current_folder)


def my_reload_callback(path):
    print('path change1: %s' % (path))


if __name__ == '__main__':
    file_monitor1 = FileMonitor(my_reload_callback)
    file_monitor1.watch('/data/projects/mydev/bb8')

    file_monitor_pool = FileMonitorPool()
    file_monitor_pool.add_file_monitor(file_monitor1)

    file_monitor_pool.start()
