import difflib
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


def show_diff(src, target):
    # src_time = parse(ctime(os.path.getmtime(src)))
    # target_time = parse(ctime(os.path.getmtime(target)))
    # print("last modified: %s" % ctime(os.path.getmtime(src)))
    # print("last modified: %s" % ctime(os.path.getmtime(target)))

    src_content = open(src).read()
    target_content = open(target).read()

    src_lines = src_content.strip().splitlines()
    target_lines = target_content.strip().splitlines()

    # print(src_time)
    #
    # if src_time > target_time:
    #     suggestion = "Use {0}".format(src)
    # else:
    #     suggestion = "Use {0}".format(target)
    #
    # print(suggestion)

    for line in difflib.unified_diff(src_lines, target_lines, fromfile=src, tofile=target, lineterm=''):
        print(line)
