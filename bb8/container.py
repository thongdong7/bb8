from bb8.core import BB8
from bb8.git import GitPush
from bb8.template import TemplateEngine
from os.path import abspath, dirname, join, expanduser

params = {
    'HOME': expanduser('~')
}

data_folder = abspath(join(dirname(__file__), '../data'))

repo_dir = abspath(dirname(__file__))
git_push = GitPush(repo_dir=repo_dir, data_folder=data_folder)

template_engine = TemplateEngine()
template_engine.load_params(params)

bb8 = BB8(template_engine=template_engine, data_folder=data_folder)
