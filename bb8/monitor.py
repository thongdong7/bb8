from six import text_type

from bb8.process.exception import CommandError
from bb8.script.utils import error_msg
from os import chdir
from time import time

import os
import yaml
from os.path import abspath, curdir, dirname, isdir, join
from os import walk

from tornado.ioloop import IOLoop, PeriodicCallback

from bb8.process.cmd import run_cmd


class FileChange(Exception):
    def __init__(self, path, *args, **kwargs):
        super(FileChange, self).__init__(path, *args, **kwargs)
        self.path = path


class FileMonitor:
    def __init__(self, callback):
        self.callback = callback
        self.watched_files = set()
        self.modify_times = {}
        self.root_path_map = {}

    def watch(self, path):
        self.watched_files.add(path)

    def watch_multiple(self, paths):
        for path in paths:
            self._add(path)

    def _add(self, path):
        if not isdir(path):
            full_path = abspath(path)
            self.root_path_map[full_path] = path
            self.watched_files.add(full_path)
        else:
            f = []
            for (dirpath, dirnames, filenames) in walk(path):
                for filename in filenames:
                    f.append(join(dirpath, filename))
                # f.extend(filenames)
            # print f

            for item in f:
                full_path = abspath(item)
                self.root_path_map[full_path] = path
                self.watched_files.add(full_path)

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

            actual_path = self.root_path_map[path]
            raise FileChange(actual_path)


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

            print('Trigger')
            for cmd in item['cmds']:
                print 'Running command: {0}'.format(cmd)
                output = run_cmd(cmd)
                print(output.encode('utf-8'))

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
                print 'Running command: {0}'.format(cmd)
                output = run_cmd(cmd)
                print(output.encode('utf-8'))
        except CommandError as e:
            error_msg(text_type(e))

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
