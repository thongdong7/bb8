import logging
import subprocess
from time import sleep, time

from .exception import CommandError


def run_cmd(cmd, **kwargs):
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, **kwargs)

    out, tmp = p.communicate()
    # print(out)
    # print(p.returncode)
    # print(p.stdout)

    if p.returncode:
        raise CommandError(cmd, out, p.returncode)

    return out.decode("utf-8")


def get_return_code(cmd, **kwargs):
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, **kwargs)

    out, tmp = p.communicate()

    return p.returncode, out.decode("utf-8")


def terminate_process(p, timeout=10, sleep_step=0.1):
    try:
        # Terminate
        p.terminate()

        for i in range(int(timeout / sleep_step)):
            exit_code = p.poll()
            if exit_code is None:
                # Still running
                sleep(sleep_step)
                continue

            print("Exit code: %s" % exit_code)
            return
    except Exception as e:
        logging.exception(e)

    try:
        # print("Kill")
        p.kill()
    except Exception as e:
        logging.exception(e)


def wait_stdout(p, text, timeout=10):
    start = time()
    stdout_lines = iter(p.stdout.readline, "")
    output = []
    for stdout_line in stdout_lines:
        line = stdout_line.decode("utf-8")[:-1]
        output.append(line)
        print(line)
        if text in line:
            return True, "\n".join(output)

        if time() - start > timeout:
            return False, "\n".join(output)

    return False, "\n".join(output)
