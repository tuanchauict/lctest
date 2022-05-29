from traceback import TracebackException

try:
    # noinspection PyUnresolvedReferences
    from StringIO import StringIO
except:
    from io import StringIO
from pygments.console import colorize
import sys
import time
import copy
import inspect

NO_RUN = 'no_run'
SOLUTION = 'solution'
TESTCASES = 'testcases'

sys.setrecursionlimit(50000)


def skip_test(fun):
    """
    Adds flag no_run to ignore executing a function for `@testcase`.
    Use this right under `@testcase` or for test method (`solXxx`)
    """

    def wrapper(*args, **kwargs):
        return fun(*args, **kwargs)

    wrapper.__dict__[NO_RUN] = True
    return wrapper


def solution(fun):
    def wrapper(*args, **kwargs):
        return fun(*args, **kwargs)

    wrapper.__dict__[SOLUTION] = True
    return wrapper


def log(*args):
    """
    Shorthand to create a testcase with log turned on.
    """
    return Testcase(args, is_log=True)


def testcase(*testcases, log=False, param_length_limit=100):
    is_printable = log or len(testcases) == 1
    if param_length_limit == -1:
        param_length_limit = float('inf')

    def deco(target):
        if inspect.isclass(target):
            deco_class(target)
        else:
            return deco_fun(target)

    def deco_fun(fun):
        def wrapper():
            execute(fun, testcases)

        is_class_method = 'self' in inspect.signature(fun).parameters
        if is_class_method or NO_RUN in fun.__dict__:
            fun.__dict__[TESTCASES] = testcases
            return fun

        print(f"{f('cyan', 'Test result for')} {f('brightgreen', f('bold', fun.__name__))}:")
        return wrapper()

    def deco_class(cls):
        def wrapper():
            for fun_name, testcases in get_runnable_methods_and_testcases():
                obj = cls()
                print(f"{f('cyan', 'Test result for')} {cls.__name__}.{f('brightgreen', f('bold', fun_name))}:")
                execute(obj.__getattribute__(fun_name), testcases)

        def get_runnable_methods_and_testcases():
            runnable_method_names_and_testcases = []

            obj = cls()
            for name in obj.__dir__():
                fun = obj.__getattribute__(name)
                if not name.startswith('sol') and SOLUTION not in dir(fun):
                    continue

                attributes = dir(fun)

                if NO_RUN in attributes or not callable(fun):
                    continue
                cases = testcases if TESTCASES not in attributes else fun.__getattribute__(TESTCASES)
                runnable_method_names_and_testcases.append((name, cases))

            return runnable_method_names_and_testcases

        if NO_RUN in dir(cls):
            return cls
        return wrapper()

    def execute(fun, testcases):
        is_method_printable = is_printable
        helper = TestHelper(testcases, is_method_printable, param_length_limit)

        for case in helper.testcases:
            printer = helper.create_case_helper(case)

            try:
                t0 = time.time()
                result = fun(*case.params_snapshot)
                runtime = (time.time() - t0) * 1000
                printer.print_result(result, runtime)
            except:
                printer.print_error()

    return deco


class _TestPrinter:
    def __init__(self, params_text, params, expected, is_test_printable):
        self.params_text = params_text
        self.params = params
        self.expected = expected
        self.is_test_printable = is_test_printable

        self.output = StringIO()

        if not is_test_printable:
            sys.stdout = self.output
        else:
            # Use gray color for log
            print(f('gray', '▼', keep_format=True))

    def print_result(self, result, runtime):
        sys.stdout = sys.__stdout__
        # Reset gray color of log
        print(f("", ""), end='')

        is_correct, formatted_result, formatted_expected = self._result_to_text(result)
        arrow = self._format(is_correct, '➜', '➜', '➜') if not callable(self.expected) else self._format(is_correct,
                                                                                                         '»', '»', '»')
        check = self._format(is_correct, '✔✔', '𐄂𐄂', '⚑⚑')

        runtime_text = f('gray', "(%.3fms)" % runtime)
        print(self.params_text, arrow, formatted_result, check, runtime_text)

        if is_correct is not None and not is_correct:
            expected_title = 'Expected:'
            space = " " * (len(self.params_text) + 2 - len(expected_title))
            print(f"{space}{f('gray', expected_title)} {formatted_expected}")

        if is_correct is None or not is_correct:
            print_log = self.output.getvalue()
            if print_log:
                print(f('brightyellow', str(print_log)))
            else:
                pass
        self.output.close()

    def _result_to_text(self, result):
        result_text = str(result)
        if self.expected is None:
            return None, result_text, ""
        if result == self.expected:
            return True, result_text, result_text

        if callable(self.expected):
            expected = self.expected(*self.params)
            expected_text = str(expected)
        else:
            expected = self.expected
            expected_text = str(self.expected)

        result_arr = []
        expected_arr = []
        length = min(len(result_text), len(expected_text))
        for i in range(length):
            is_equal = result_text[i] == expected_text[i]
            result_arr.append(result_text[i] if is_equal else f('red', result_text[i]))
            expected_arr.append(expected_text[i] if is_equal else f('red', expected_text[i]))
        if length < len(result_text):
            result_arr.append(f('red', result_text[length:]))
        else:
            expected_arr.append(f('red', expected_text[length:]))
        return expected == result, "".join(result_arr), "".join(expected_arr)

    @staticmethod
    def _format(is_correct, correct, wrong, unknown):
        if is_correct is None:
            return f('yellow', unknown)
        elif is_correct:
            return f('green', correct)
        else:
            return f('red', wrong)

    def print_error(self):
        print_log = self.output.getvalue().strip()
        sys.stdout = sys.__stdout__
        print(self.params_text)
        if print_log:
            print(print_log)
        exec_info = sys.exc_info()
        traceback_lines = list(TracebackException(*exec_info).format())
        trimmed_traceback_lines = []
        for line in traceback_lines[::-1]:
            if "test/testcase.py" in line:
                break
            if len(trimmed_traceback_lines) > 5:
                break
            trimmed_traceback_lines.insert(0, line)
        for line in trimmed_traceback_lines:
            print(f('red', line), end="")
        print()


class TestHelper:

    def __init__(self, testcases, is_test_printable, param_length_limit):
        self.testcases = [tc if isinstance(tc, Testcase) else Testcase(tc) for tc in testcases]
        self.param_length_limit = param_length_limit
        self.param_format = self._build_format()
        self.is_test_printable = is_test_printable

    def _build_format(self):
        param_count = len(self.testcases[0].params)
        param_lengths = [0] * param_count

        for case in self.testcases:
            for i, param in enumerate(case.params):
                str_param = str(param)
                param_lengths[i] = min(max(param_lengths[i], len(str_param)), self.param_length_limit)

        total_space = sum(param_lengths) + 4 * (len(param_lengths) - 1)
        prefix = " " * (8 - total_space)
        param_formats = [f"{prefix}%{length}s" for length in param_lengths]

        return "    ".join(param_formats)

    def create_case_helper(self, testcase):
        param_texts = [str(param) for param in testcase.params]
        for i, text in enumerate(param_texts):
            param_texts[i] = text if len(text) < self.param_length_limit else text[:self.param_length_limit - 3] + "..."

        params_text = self.param_format % tuple(param_texts)
        is_case_loggable = self.is_test_printable or testcase.is_loggable
        return _TestPrinter(params_text, testcase.params, testcase.expected, is_case_loggable)


class Testcase:
    def __init__(self, args, is_log=False):
        self.expected = args[0]
        self.params = args[1:]
        self.is_loggable = is_log

    @property
    def params_snapshot(self):
        return copy.deepcopy(self.params)


def f(color, text, keep_format=False):
    formatted_text = colorize(color, text)
    return formatted_text if not keep_format else formatted_text[:-11]
