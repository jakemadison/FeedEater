__author__ = 'jmadison'

from os.path import dirname
from sys import path
path.append(dirname(dirname(__file__)))

print "so far so good....."

import os.path
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from feedeater.config import configs

basedir = configs.get('basedir')

print 'naaaaam!:::::::', __name__
flaskapp = Flask(__name__)
flaskapp.config.from_object('feedeater.config')
db = SQLAlchemy(flaskapp)

lm = LoginManager()
lm.init_app(flaskapp)
lm.login_view = 'login'
oid = OpenID(flaskapp, os.path.join(basedir, 'tmp'))
import feedeater.display.views






