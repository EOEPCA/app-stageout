from setuptools import setup, find_packages
from io import open
import os

print(find_packages(where='src'))

console_scripts = """
[console_scripts]
stage-out=outstac.__init__:main
"""

setup(entry_points=console_scripts,
      packages=find_packages(where='src'),
      package_dir={'': 'src'})


