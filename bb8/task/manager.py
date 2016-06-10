import logging
import subprocess
from subprocess import Popen

import yaml
from bb8.process.cmd import terminate_process, run_cmd, wait_stdout
from bb8.script.utils import write_msg
from bb8.task.exception import RunServiceError, TaskError
from jinja2 import Template


class Task(object):
    def __init__(self, config, params={}):
        if isinstance(config, list):
            tmp_config = {
                'before': None,
                'after': None,
                'actions': config
            }
        elif isinstance(config, dict):
            tmp_config = config
        else:
            raise TaskError(config)

        content = Template(yaml.dump(tmp_config)).render(**params)
        tmp_config = yaml.load(content)

        self.before = tmp_config.get('before')
        self.after = tmp_config.get('after')

        self.actions = tmp_config.get('actions')


class TaskActionExecutor(object):
    def __init__(self, actions):
        self.actions = actions
        self.services = {}

        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self):
        # has_error = None
        # try:
        #     # Get before

        for item in self.actions:
            # print item

            if 'service' in item:
                self.run_service(item)
            else:
                self.run_command(item)

        write_msg("Task completed")
        # except RunServiceError as e:
        #     has_error = True
        #     error_msg(str(e))
        # except CommandError as e:
        #     has_error = True
        #     exit_msg(str(e))
        # finally:
        #     self.stop()
        #
        #     if has_error:
        #         error_msg("Completed with error")
        #     else:
        #         msg = "Completed successful"
        #         write_msg(msg)

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


class TaskManager(object):
    def __init__(self, task_map):
        self.task_map = task_map

        self.action_executors = []

    def _execute(self, task_settings, params={}):
        # print("Execute task: {0}. Params: {1}".format(task_settings, params))
        if isinstance(task_settings, str):
            task_settings = {
                'task': task_settings
            }

        assert 'task' in task_settings, "Missed task name in task_settings {0}".format(task_settings)
        task_name = task_settings['task']
        task_params = task_settings.get('params', {})
        for field_name in params:
            if field_name not in task_params:
                task_params[field_name] = params[field_name]

        config = self.task_map[task_name]
        config_params = config.get('params', {})
        for field_name in config_params:
            if field_name not in task_params:
                task_params[field_name] = config_params[field_name]
        # print("Task params: {0}".format(task_params))

        task = Task(config, params=task_params)

        # Execute before
        if task.before:
            self._execute(task.before, params=task_params)

        # Execute actions
        action_executor = TaskActionExecutor(task.actions)
        self.action_executors.append(action_executor)

        action_executor.execute()

        if task.after:
            self._execute(task.after, params=task_params)

    def execute(self, task_name):
        try:
            self._execute(task_name)
        finally:
            for action_executor in self.action_executors:
                try:
                    action_executor.stop()
                except:
                    pass
