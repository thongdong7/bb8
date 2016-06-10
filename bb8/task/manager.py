import logging
import subprocess
from subprocess import Popen

from bb8.process.cmd import terminate_process, run_cmd, wait_stdout
from bb8.process.exception import CommandError
from bb8.script.utils import exit_msg, write_msg, error_msg


class RunServiceError(Exception):
    def __init__(self, task, output, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output = output
        self.task = task


class TaskManager(object):
    def __init__(self, tasks):
        assert isinstance(tasks, list)

        self.tasks = tasks
        self.services = {}

        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self):
        has_error = None
        try:
            for item in self.tasks:
                # print item

                if 'service' in item:
                    self.run_service(item)
                else:
                    self.run_command(item)

            write_msg("Task completed")
        except RunServiceError as e:
            has_error = True
            error_msg(str(e))
        except CommandError as e:
            has_error = True
            exit_msg(str(e))
        finally:
            self.stop()

            if has_error:
                error_msg("Completed with error")
            else:
                msg = "Completed successful"
                write_msg(msg)

    def stop(self):
        write_msg("Stop services")
        for service_name in self.services:
            try:
                write_msg("Stop service: %s" % service_name)
                terminate_process(self.services[service_name])
            except:
                pass

    def run_service(self, task):
        p = Popen(task['cmd'], shell=True, stderr=subprocess.STDOUT,
                  stdout=subprocess.PIPE)

        self.services[task['service']] = p

        if 'wait_stdout' in task:
            ok, output = wait_stdout(p, task['wait_stdout'], timeout=task.get('wait_stdout_timeout', 10))
            if not ok:
                raise RunServiceError(task, output=output)

    def run_command(self, task):
        write_msg("--- Run command: {0} ---".format(task['cmd']))
        cmd_output = run_cmd(task['cmd'])
        cmd_output_items = cmd_output.split('\n')
        output_items = ['\t%s' % _ for _ in cmd_output_items]
        write_msg('\n'.join(output_items))
