import os

from codecs import open

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'interpreter', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(name=about['__title__'],
      version=about['__version__'],
      long_description=readme,
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False)
