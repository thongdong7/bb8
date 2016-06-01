class CommandError(Exception):
    def __init__(self, cmd, output, returncode, *args, **kwargs):
        super(CommandError, self).__init__(*args, **kwargs)
        self.cmd = cmd
        self.output = output.decode("utf-8")
        self.returncode = returncode

    def __str__(self, *args, **kwargs):
        return self.__repr__()

    def __repr__(self, *args, **kwargs):
        return 'Command Error: {0}\nCommand: {1}\nDetail: {2}' \
            .format(self.returncode, self.cmd, self.output)
