import logging
from time import sleep

import click as click
import yaml

from bb8.process.cmd import get_return_code
from bb8.script.config import default_config_file


class CheckResult:
    def __init__(self):
        self.last_failed = 0
        self.last_output = None

    def add(self, return_code, output):
        self.last_output = output
        if return_code:
            self.last_failed += 1
        else:
            self.last_failed = 0

    @property
    def ok(self):
        return self.last_failed == 0

    def __repr__(self, *args, **kwargs):
        return self.__str__(*args, **kwargs)

    def __str__(self, *args, **kwargs):
        if self.ok:
            return "OK"
        else:
            return "FAILED {0} times. Output: {1}".format(self.last_failed, self.last_output)


class FailedMon(object):
    def __init__(self, item):
        self.item = item
        self.check_result = CheckResult()
        self.failed_result = CheckResult()

    def check(self):
        check_return_code, check_out = get_return_code(self.item['check'])

        self.check_result.add(check_return_code, check_out)

    def execute_on_failed(self):
        print("Run {0}".format(self.item['failed']))
        failed_rc, failed_out = get_return_code(self.item['failed'])
        self.failed_result.add(failed_rc, failed_out)
        # if failed_rc:
        #     print("Run failed command FAILED. {0}".format(failed_out))


class FailedMonManager:
    def __init__(self, items, check_only):
        assert isinstance(items, list)
        self.check_only = check_only

        self.mons = {}
        for item in items:
            check_name = item['name']
            self.mons[check_name] = FailedMon(item)

        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self):
        for check_name in self.mons:
            try:
                mon = self.mons[check_name]
                mon.check()

                print("Check {0}: {1}".format(check_name, mon.check_result))

                if self.check_only:
                    continue

                if not mon.check_result.ok:
                    mon.execute_on_failed()

                    print(mon.failed_result)
            except Exception as e:
                self.logger.error("Check {0} failed".format(check_name))
                self.logger.exception(e)


@click.command('failed-mon', help='Run check, if failed, run ')
@click.option('--check', 'check_only', is_flag=True, help='Check then exit')
@click.option('--sleep', '-s', 'sleep_time', default=5 * 60, help='Sleep time')
@click.option('--config', '-c', 'config_file', default=default_config_file, help='Path to config file')
def failed_monitor(config_file, check_only, sleep_time):
    data = yaml.load(open(config_file))
    items = data['failed-monitor']
    failed_mon_manager = FailedMonManager(items, check_only=check_only)
    while True:
        failed_mon_manager.execute()
        # for item in items:
            # try:
            #     check_name = item['name']
            #     check_return_code, check_out = get_return_code(item['check'])
            #
            #     if check_return_code:
            #         print("Check {0}: FAILED ({1}). Out: {2}".format(check_name, check_return_code, check_out))
            #
            #         if check_only:
            #             continue
            #
            #         print("Run {0}".format(item['failed']))
            #         failed_rc, failed_out = get_return_code(item['failed'])
            #         if failed_rc:
            #             print("Run failed command FAILED. {0}".format(failed_out))
            #
            #         print(failed_out)
            #     else:
            #         print("Check {0}: PASSED".format(check_name))
            # except Exception as e:
            #     logging.error("Error on %s" % item)
            #     logging.error(e)

        print("Sleep %s before check again" % sleep_time)
        sleep(sleep_time)
    # print(data)
