#!feedgetter_env/bin/python

import sys
for e in sys.path:
    print e

from FeedGetter import create_app

if __name__ == "__main__":
    flaskapp = create_app()
    print flaskapp
    flaskapp.run(debug = True)