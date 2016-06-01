from bb8.process.cmd import run_cmd
from bb8.process.exception import CommandError
from bb8.script.utils import write_msg


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


class MissedKillError(Exception):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def __str__(self, *args, **kwargs):
        return "Missed skill '{0}'. Why don't you to add one?".format(self.name)

    def __repr__(self, *args, **kwargs):
        return super().__str__(*args, **kwargs)


class SkillManager(object):
    def __init__(self):
        self.skill_map = {}

        self.load_skills()

    def load_skills(self):
        data = [
            {
                "name": "rerun docker",
                "use": "dc stop $1 && dc rm -f $1 && dc up -d $1"
            }
        ]

        for item in data:
            name = item['name']
            skill = Skill(item)
            self.skill_map[name] = skill

    def execute(self, *args):
        name, skill_args = self.parse_request(*args)
        self.execute_skill(name, *skill_args)

    def parse_request(self, *args):
        for i in reversed(range(len(args) + 1)):
            quest_name = ' '.join(args[:i])
            if quest_name in self.skill_map:
                return quest_name, args[i:]

        raise MissedKillError(' '.join(args))

    def get_skill(self, name):
        return self.skill_map.get(name)

    def execute_skill(self, name, *args, **kwargs):
        skill = self.get_skill(name)

        if not skill:
            # Don't have that skill yet
            raise MissedKillError(name=name)

        use = skill.use

        for i, arg in enumerate(args):
            use = use.replace('${0}'.format(i + 1), arg)

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
