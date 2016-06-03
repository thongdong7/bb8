from os import makedirs
from os.path import dirname, exists


def is_diff(local_file, remote_file):
    if not exists(remote_file):
        return True

    return open(remote_file, ).read() != open(local_file).read()


def copy_file(local_file, remote_file):
    remote_dir = dirname(remote_file)
    if not exists(remote_dir):
        makedirs(remote_dir)

    open(remote_file, 'w').write(open(local_file).read())
