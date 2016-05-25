import logging

import os
from genericpath import exists
from os.path import join, dirname


class BB8(object):
    def __init__(self, template_engine, data_folder):
        self.data_folder = data_folder
        self.template_engine = template_engine

        self.logger = logging.getLogger(self.__class__.__name__)

    def merge_file(self, local_file, remote_file):
        self.logger.debug('Merge file %s' % local_file)
        open(remote_file, 'w').write(open(local_file).read())

    def get_monitor_files(self, paths):
        for path in paths:
            local_file = self.template_engine.render(path)
            yield local_file

    def _is_diff(self, local_file, remote_file):
        if not exists(remote_file):
            return True

        return open(remote_file, ).read() != open(local_file).read()

    def _get_changes(self, paths):
        """
        Return changed files in paths.

        :param paths:
        :type paths:
        :return:
        :rtype:
        """
        for path in paths:
            local_file = self.template_engine.render(path)
            # print(real_path)
            if not exists(local_file):
                continue

            remote_file = join(self.data_folder, path[1:])
            # print(remote_file)

            if not self._is_diff(local_file, remote_file):
                # No thing change
                continue

            yield local_file, remote_file

    def sync_paths(self, paths):
        change = False

        for local_file, remote_file in self._get_changes(paths):
            output_dir = dirname(remote_file)
            if not exists(output_dir):
                os.makedirs(output_dir)

            if exists(remote_file):
                self.merge_file(local_file, remote_file)
            else:
                self.copy_file(local_file, remote_file)

            change = True

        return change

    def copy_file(self, local_file, remote_file):
        self.logger.debug('Copy file %s' % local_file)
        open(remote_file, 'w').write(open(local_file).read())
