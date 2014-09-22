#!../../feed_env/bin/python
from __future__ import print_function

import argparse

# Specify port number (5000 by default)
parser = argparse.ArgumentParser(description='Launch FeedEater Application')
parser.add_argument('-p', '--port', help='Specify Port Number', required=False, default=5000)
parser.add_argument('-v', '--verbose', help='Increase verbosity of logging (currently does nothing)',
                    required=False, default=5000)

args = parser.parse_args()

# Room for more command line options here.  Debug?

from feedeater import flaskapp

try:
    flaskapp.run(debug=True, port=int(args.port))

# this should be a more specific exception:
except Exception, e:
    print("Error Launching FeedEater: {0}".format(str(e)))