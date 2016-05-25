from jinja2 import Template


class TemplateEngine(object):
    def __init__(self):
        self.params = {}

    def load_params(self, params):
        self.params.update(params)

    def render(self, text):
        return Template(text).render(**self.params)
