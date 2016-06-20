import shlex

import yaml
from bb8.process.cmd import run_cmd
from bb8.process.exception import CommandError
from bb8.script.utils import write_msg, error_msg
from os import makedirs, walk
from os.path import expanduser, exists, join
from yaml.scanner import ScannerError


class Skill(object):
    def __init__(self, config):
        self.config = config

    @property
    def name(self):
        return self.config['name']

    @property
    def use(self):
        return self.config['use']


class SkillExecuteError(Exception):
    def __init__(self, skill, use, detail, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skill = skill
        self.use = use
        self.detail = detail

    def __str__(self, *args, **kwargs):
        return "Could not execute skill '{0}'. Use: '{1}'. Detail: '{2}'".format(self.skill.name, self.use, self.detail)

    def __repr__(self, *args, **kwargs):
        return super().__str__(*args, **kwargs)


class MissedSkillError(Exception):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def __str__(self, *args, **kwargs):
        return "Missed skill '{0}'. Why don't you to add one?".format(self.name)

    def __repr__(self, *args, **kwargs):
        return super().__str__(*args, **kwargs)


class SkillFileError(Exception):
    pass


class SkillManager(object):
    def __init__(self):
        self.skill_map = {}

        self.load_skills()

    def load_skills(self):
        skill_dir = expanduser('~/.bb8/skills')
        # print(skill_dir)
        if not exists(skill_dir):
            makedirs(skill_dir)

        data = self._load_skills_from_folder(skill_dir)

        data += [
            {
                "name": "rerun docker",
                "use": "dc stop $1 && dc rm -f $1 && dc up -d $1"
            }
        ]

        # pprint(data)
        # sys.exit(1)

        for item in data:
            name = item['name']
            skill = Skill(item)
            self.skill_map[name] = skill

    def _load_skills_from_folder(self, skill_dir):
        ret = []

        for dirName, subdirList, fileList in walk(skill_dir):
            # print('Found directory: %s' % dirName)
            for fname in fileList:
                # print('\t%s' % fname)
                path = join(dirName, fname)
                try:
                    ret += self._load_skill_from_file(path)
                except SkillFileError as e:
                    error_msg('SkillFileError: {0}'.format(str(e)))

        return ret

    def _load_skill_from_file(self, path):
        try:
            return yaml.load(open(path))
        except ScannerError as e:
            raise SkillFileError(str(e))


    def execute(self, *args):
        name, skill_args = self.parse_request(*args)
        self.execute_skill(name, *skill_args)

    def parse_request(self, *args):
        for i in reversed(range(len(args) + 1)):
            quest_name = ' '.join(args[:i])
            if quest_name in self.skill_map:
                return quest_name, args[i:]

        raise MissedSkillError(' '.join(args))

    def command_to_use(self, command):
        args = shlex.split(command)
        try:
            name, skill_args = self.parse_request(*args)
            skill = self.get_skill(name)
            return self._build_use_command(skill.use, skill_args)
        except MissedSkillError:
            return None

    def get_skill(self, name):
        return self.skill_map.get(name)

    def _build_use_command(self, use, args):
        for i, arg in enumerate(args):
            use = use.replace('${0}'.format(i + 1), arg)

        return use

    def execute_skill(self, name, *args, **kwargs):
        skill = self.get_skill(name)

        if not skill:
            # Don't have that skill yet
            raise MissedSkillError(name=name)

        use = skill.use

        # for i, arg in enumerate(args):
        #     use = use.replace('${0}'.format(i + 1), arg)
        use = self._build_use_command(use, args)

        # print(use)
        # print(skill.use)

        try:
            run_cmd(use)
        except CommandError as e:
            raise SkillExecuteError(skill=skill, use=use, detail=e.output)

        write_msg("Complete: {0}".format(use))

# def cli_run_skill(name):
#     skill_manager = SkillManager()
#     try:
#         skill_manager.execute(*sys.argv[1:])
#     except (SkillExecuteError, MissedKillError) as e:
#         exit_msg(str(e))
#     return
#
# if __name__ == '__main__':
#     cli_run_skill("rerun docker")
