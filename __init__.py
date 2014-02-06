# add project root folder to pythonpath

from os.path import dirname
from sys import path

path.append(dirname(dirname(__file__)))

# TODO: might be a good idea to incorporate a webpage craweler to attempt to find
# RSS links within the page.  could return multiple results and ask user to pick
# between them.