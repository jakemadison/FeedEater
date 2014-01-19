# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from flask.ext.sqlalchemy import SQLAlchemy
# from flask import Flask
#
#
#
# app = Flask(__name__)
# # controller.config.from_object('dbconfig')
# basedir = os.path.abspath(os.path.dirname(__file__))
#
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'controller.db')
# SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
# db_connector = SQLALCHEMY_DATABASE_URI
#
#
# engine = create_engine(db_connector,
#                        convert_unicode=True)
#                        # sqllite does not do pool size
#                        # pool_size=configs.get("reader_threads"))
#
# db_session = scoped_session(sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=engine))
#
# Model = declarative_base()
# Model.query = db_session.query_property()
# dbmodel = SQLAlchemy(app)
#
# # this needs to be done to properly register metadata!!!
#
# import models