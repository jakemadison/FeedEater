# add project root folder to pythonpath

from os.path import dirname
from sys import path

path.append(dirname(dirname(__file__)))