# from flask import Flask
# from flask.ext.sqlalchemy import SQLAlchemy
#
# controller = Flask(__name__)
# controller.config.from_object('display.config')
# db = SQLAlchemy(controller)
#
# import os
# from flask.ext.login import LoginManager
# from flask.ext.openid import OpenID
# from config import basedir
#
# lm = LoginManager()
# lm.init_app(controller)
# lm.login_view = 'login'
# oid = OpenID(controller, os.path.join(basedir, 'tmp'))
#
# from display import views
