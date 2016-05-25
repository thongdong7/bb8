from bb8.process.cmd import run_cmd


class GitPush(object):
    def __init__(self, repo_dir, data_folder, silent=True):
        self.silent = silent
        self.repo_dir = repo_dir
        self.data_folder = data_folder

    def commit_and_push(self):
        cmds = [
            'git add -A {0}'.format(self.data_folder),
            # 'git status',
            'git commit -m "Add files"',
            'git push'
            # 'lsa /'
        ]

        for cmd in cmds:
            out = run_cmd(cmd, cwd=self.repo_dir)
            if not self.silent:
                print(out)
