__author__ = 'jmadison'

# add project root folder to pythonpath
from os.path import dirname
from sys import path

path.append(dirname(__file__))

import os.path
import database.models
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from display.config import basedir

flaskapp = Flask(__name__)
flaskapp.config.from_object('database.dbconfig')

lm = LoginManager()
lm.init_app(flaskapp)
lm.login_view = 'login'
oid = OpenID(flaskapp, os.path.join(basedir, 'tmp'))

db = SQLAlchemy(flaskapp)

from display import views







