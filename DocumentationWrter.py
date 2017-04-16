import inspect
from functools import reduce

from rx import Observable


def tab():
    return '    '


def add_decorators(template, args):
    first_arg = args[0]
    if first_arg == 'cls':
        return '@classmethod' + '\n' + template
    if first_arg not in ['self', 'cls']:
        return '@staticmethod' + '\n' + template
    return template


def alter_special_args(args_str):
    return args_str \
        .replace("'", "") \
        .replace("scheduler", "scheduler=None") \
        .replace(", subscribe", "") \
        .replace(", factory", "") \
        .replace("self,)", "self)")


public_methods = ((name, method) for name, method in inspect.getmembers(Observable) if not name.startswith('_'))
formatted_methods = []
for name, method in public_methods:
    args = method.__code__.co_varnames
    args_str = alter_special_args(str(args))
    doc = method.__doc__
    doc_str = f'"""\n{tab()}{doc}"""\n{tab()}' if doc else ''
    template = f"def {name}{args_str}:\n{tab()}{doc_str}pass"
    template = add_decorators(template, args)
    formatted_methods.append(template)

methods_str = '\n\n' + reduce(lambda a, b: a + '\n\n' + b, [tab() + method.replace('\n', '\n' + tab()) for method in formatted_methods])

from os import path

path_observable = path.abspath('rx/core/py3/observable.py')
with open(path_observable, mode='a') as f:
    f.write(methods_str)
