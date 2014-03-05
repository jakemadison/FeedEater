__author__ = 'jmadison'

#add project root to PYTHONPATH:
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
print basedir

flaskapp = Flask('feedeater', static_folder=basedir+'/display/static', template_folder=basedir+'/display/templates')
flaskapp.config.from_object('feedeater.config')


db = SQLAlchemy(flaskapp)
import database.models

lm = LoginManager()
lm.init_app(flaskapp)
lm.login_view = 'login'
oid = OpenID(flaskapp, os.path.join(basedir, 'tmp'))

from feedeater.display.views import main, subscriptions, entries, custom_filters

flaskapp.register_blueprint(main.app)
flaskapp.register_blueprint(subscriptions.app)
flaskapp.register_blueprint(entries.app)

flaskapp.jinja_env.filters['truncate_title'] = custom_filters.truncate_title



