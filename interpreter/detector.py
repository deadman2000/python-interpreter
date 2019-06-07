import importlib.util
import os
import inspect
from structure import Element

all_modules = []


def load_modules(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                module_name = file[:-3]
                spec = importlib.util.spec_from_file_location(module_name, os.path.join(root, file))
                foo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(foo)
                for name, obj in inspect.getmembers(foo, inspect.isclass):
                    if obj.__module__ == module_name and issubclass(obj, Element):
                        print(file, name)


def parse_file(path, **kwargs):
    with open(path, "rb") as file:
        el = None
        return el.parse_stream(file, **kwargs)


if __name__ == '__main__':
    load_modules('formats')
