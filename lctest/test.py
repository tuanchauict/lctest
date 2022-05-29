from random import Random
import typing

from pygments.console import colorize as f

import time
import json

from lctest.lib import linked_list_to_array


def audit(text=''):
    global t0
    if text:
        runtime = (time.time() - t0) * 1000
        print(f"{text}: {'%.6f' % runtime} ms")
    t0 = time.time()


def linked_list_result_to_array(fun):
    def wrapper(*args, **kwargs):
        head = fun(*args, **kwargs)
        return linked_list_to_array(head)

    return wrapper


def list_node_to_value(fun):
    def wrapper(*args, **kwargs):
        node = fun(*args, **kwargs)

        return node.val if node else None

    return wrapper


def sort_result(fun):
    def wrapper(*args, **kwargs):
        arr = fun(*args, **kwargs)
        return sorted(arr)

    return wrapper


def run(times=1):
    def deco(fun):
        import inspect
        has_parameter = len(inspect.signature(fun).parameters) > 0

        def wrapper():
            print(f"Running {f('green', f('bold', fun.__name__))}")
            for i in range(times):
                print(f("gray", f"---------#{i + 1}---------"))
                args = [i] if has_parameter else []
                fun(*args)

        return wrapper()

    return deco


def measure(fun, *args):
    t0 = time.time()
    result = fun(*args)
    run_time = time.time() - t0
    return run_time, result


def random_list(size, min_value, max_value=1000, seed=None, is_sorted=False):
    if isinstance(min_value, typing.Iterable):
        space = list(min_value)
        min_value = 0
        max_value = len(space) - 1
    else:
        space = None

    r = Random(seed) if seed is not None else Random()
    arr = [r.randint(min_value, max_value) for _ in range(size)]
    if space:
        arr = [space[i] for i in arr]
    return sorted(arr) if is_sorted else arr


def random_matrix(row, col, min_value, max_value, seed=None):
    r = Random(seed) if seed is not None else Random()
    return [
        [r.randint(min_value, max_value) for _ in range(col)]
        for _ in range(row)
    ]


def print_json(obj, indent=4):
    print(json.dumps(obj, indent=indent))
