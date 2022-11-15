from ruamel import yaml
import re
import os
os.system('pip install ruamel.yaml')

def isnumber(s):
    return s and re.match('^\d*(\.\d*)?$',s)

def get(dict_, keys, default=None):
    res=dict_.get(keys,default)
    if res and isnumber(res):
        if '.' in res:
            return float(res)
        else:
            return int(res)
    return res 


class Subtask:
    def __init__(self, id_, conf, is_ex=False, type_='min', score='none'):
        self.id_ = id_
        self.depends = []
        self.points = []
        self.is_ex = is_ex
        self.memory = get(conf, f'subtask_memory_limit_{id_}') or get(
            conf, f'memory_limit')
        self.time = get(conf, f'subtask_time_limit_{id_}') or get(
            conf, f'time_limit')
        self.score = float(
            get(conf, f'subtask_score_{id_}')) if score == 'none' else score
        self.type_ = type_

    def init_problem(self, conf, p):
        self.points = []
        while p <= (get(conf, f'subtask_end_{self.id_}') or get(conf, 'n_tests')):
            self.points.append(Point(p, self.id_, conf, self.is_ex))
            p += 1
        return p

    def init_depends(self, conf):
        depend = get(conf, f'subtask_dependence_{self.id_}')
        if depend:
            if depend == 'many':
                q = 1
                while get(conf, f'subtask_dependence_{self.id_}_{q}'):
                    self.depends.append(
                        int(get(conf, f'subtask_dependence_{self.id_}_{q}')))
                    q += 1
            else:
                self.depends.append(int(depend))

    def export(self):
        return {
            'score': int(self.score),
            'type': self.type_,
            'time':f'{self.time*1000}ms',
            'memory': f'{self.memory}m',
            'cases': [point.export() for point in self.points],
            'if': self.depends
        }


class Point:
    def __init__(self, id_, sub, conf, is_ex=False):
        self.id_ = id_
        self.sub = sub
        self.score = get(conf, f'point_score_{id_}') or get(
            conf, f'subtask_score_{sub}') or 100//get(conf, f'n_tests')
        self.time = get(conf, f'point_time_limit_{id_}') or get(
            conf, f'subtask_time_limit_{sub}') or get(conf, f'time_limit')
        self.memory = get(conf, f'point_memory_limit_{id_}') or get(
            conf, f'subtask_memory_limit_{sub}') or get(conf, f'memory_limit')
        self.input = ('ex_' if is_ex else '') + \
            get(conf, 'input_pre')+str(id_)+'.'+get(conf, 'input_suf')
        self.output = ('ex_' if is_ex else '') + \
            get(conf, 'output_pre')+str(id_)+'.'+get(conf, 'output_suf')

    def export(self):
        return {
            'score': self.score,
            'time':f'{self.time*1000}ms',
            'memory': f'{self.memory}m',
            'input': self.input,
            'output': self.output
        }


class ParseHelper:
    def __init__(self, s):
        self.s = s
        self.p = 0

    def not_token(self, c):
        return c in (' ', '\n', '\t', '\r')

    def readtoken(self):
        if self.p == len(self.s):
            return (False, 0)
        while self.p < len(self.s) and self.not_token(self.s[self.p]):
            self.p += 1
        s = ''
        while self.p < len(self.s) and not self.not_token(self.s[self.p]):
            s += self.s[self.p]
            self.p += 1
        return (True, s)

    def getdict(self):
        res = {}
        while self.p != len(self.s):
            key = self.readtoken()[1]
            value = self.readtoken()[1]
            res[key]=value
        return res

    def parse_tasks(self, conf):
        cnt = get(conf, 'n_subtasks', 0)
        tasks = []

        ex_task = Subtask(cnt+1, conf, 0, score=3)
        p = 1
        if get(conf, 'n_sample_tests'):
            for i in range(1, 1+get(conf, 'n_sample_tests')):
                ex_task.points.append(
                    Point(i, 0, conf, True)
                )
        if get(conf, 'n_ex_tests'):
            for i in range(get(conf, 'n_sample_tests', 0)+1, 1+get(conf, 'n_ex_tests')):
                ex_task.points.append(
                    Point(i, 0, conf, True)
                )

        tasks.append(ex_task)

        p = 1
        for i in range(1, cnt+1):
            task = Subtask(i, conf)
            p = task.init_problem(conf, p)
            task.init_depends(conf)
            tasks.append(task)

        other_task = Subtask(cnt+2, conf, False, 'sum', score='100')
        other_task.init_problem(conf, p)
        tasks.append(other_task)

        return tasks

    def export(self, tasks, file, conf, is_spj):
        config = {
            'type': 'default',
            'checker_type': 'default',
            'subtasks': []
        }
        for task in tasks:
            if task.points:
                config['subtasks'].append(task.export())
        if is_spj:
            config['checker'] = 'chk.cpp'
            config['checker_type'] = 'testlib'
        if get(conf, 'use_builtin_checker'):
            config['checker'] = get(conf, 'use_builtin_checker')
            config['checker_type'] = 'testlib'
        return True, yaml.dump(config, file, Dumper=yaml.RoundTripDumper)


def convert(p):
    with open(os.path.join(p, 'problem.conf')) as f:
        content = f.read()
    is_spj = os.path.exists(os.path.join(p, 'chk.cpp'))
    ph = ParseHelper(content)

    conf = ph.getdict()
    if conf.get('with_implementer', 'off') == 'on':
        return False
    if conf.get('submit_answer', 'off') == 'on':
        return False

    tasks = ph.parse_tasks(conf)
    with open(os.path.join(p, 'config.yaml'), 'w') as f:
        ph.export(tasks, f, conf, is_spj)
    os.remove(os.path.join(p, 'problem.conf'))
    return True
