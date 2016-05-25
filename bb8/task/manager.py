import logging
import subprocess
from subprocess import Popen

from bb8.process.cmd import terminate_process, run_cmd


class TaskManager(object):
    def __init__(self, tasks):
        assert isinstance(tasks, list)

        self.tasks = tasks
        self.services = {}

        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self):
        try:
            for item in self.tasks:
                # print item

                if 'service' in item:
                    self.run_service(item)
                else:
                    self.run_command(item)
        finally:
            self.stop()

    def stop(self):
        for service_name in self.services:
            try:
                self.logger.debug("Stop service: %s" % service_name)
                terminate_process(self.services[service_name])
            except:
                pass

    def run_service(self, task):
        self.services[task['service']] = Popen(task['cmd'], shell=True, stderr=subprocess.STDOUT,
                                               stdout=subprocess.PIPE)

    def run_command(self, task):
        print(run_cmd(task['cmd']))
