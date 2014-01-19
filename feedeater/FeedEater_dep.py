#!feedgetter/bin/python
#Because sometimes it's fun to reinvent the wheel.

import os.path
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from feedeater.display.config import basedir


def create_app():

    flaskapp = Flask(__name__)
    flaskapp.config.from_object('database.dbconfig')

    lm = LoginManager()
    lm.init_app(flaskapp)
    lm.login_view = 'login'
    oid = OpenID(flaskapp, os.path.join(basedir, 'tmp'))

    db = SQLAlchemy(flaskapp)

    return flaskapp


if __name__ == "__main__":
    print 'Running.....'
