#!feedgetter_env/bin/python

import sys
for e in sys.path:
    print e

from feedeater import config

from feedeater import flaskapp

flaskapp.run(debug = True)