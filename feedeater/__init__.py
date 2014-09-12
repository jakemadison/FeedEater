__author__ = 'jmadison'

print '\n\n\n\n'
import logging


def setup_logger(logger_instance, level):

    if logger.handlers:  # prevents the loading of duplicate handlers/log output
        return

    logger_instance.setLevel(level)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('(%(asctime)s: %(name)s: %(levelname)s): %(message)s')
    ch.setFormatter(formatter)
    logger_instance.addHandler(ch)


logger = logging.getLogger(__name__)
setup_logger(logger, logging.DEBUG)
logger.info('completed logger config.  beginning to load application.')

#add project root to PYTHONPATH:
#apparently this ain't working..
from os.path import dirname
from sys import path
path.append(dirname(dirname(__file__)))


import os.path
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from feedeater.config import configs

basedir = configs.get('basedir')

logger.debug('basedir is '+ basedir)

flaskapp = Flask('feedeater', static_folder=basedir+'/display/static', template_folder=basedir+'/display/templates')
flaskapp.config.from_object('feedeater.config')


db = SQLAlchemy(flaskapp)
#import database.models


lm = LoginManager()
lm.init_app(flaskapp)
lm.login_view = 'login'
oid = OpenID(flaskapp, os.path.join(basedir, 'tmp'))


from feedeater.display.views import main, subscriptions, entries, custom_filters


# register blueprints
flaskapp.register_blueprint(main.app)
flaskapp.register_blueprint(subscriptions.app)
flaskapp.register_blueprint(entries.app)


# register custom template filters:
flaskapp.jinja_env.filters['truncate_title'] = custom_filters.truncate_title
flaskapp.jinja_env.filters['parse_time'] = custom_filters.parse_time
flaskapp.jinja_env.filters['url_base'] = custom_filters.url_base

logger.info('finished loading app.')