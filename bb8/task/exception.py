class RunServiceError(Exception):
    def __init__(self, task, output, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output = output
        self.task = task


class TaskError(Exception):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

    def __str__(self, *args, **kwargs):
        return "Un-supported task config with type: {0}".format(self.config.__class__)

    def __repr__(self, *args, **kwargs):
        return super().__str__(*args, **kwargs)
