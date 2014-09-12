import os
basedir = os.path.abspath(os.path.dirname(__file__))

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#from flask.ext.sqlalchemy import SQLAlchemy
#from flask import Flask

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database/app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'database/db_repository')

ver = "0.0.0"

configs = {

    "User-Agent": "feed_getter.v{0}".format(ver),
    "SQLALCHEMY_DATABASE_URI": SQLALCHEMY_DATABASE_URI,
    "SQLALCHEMY_MIGRATE_REPO": SQLALCHEMY_MIGRATE_REPO,
    "db_connector": SQLALCHEMY_DATABASE_URI,
    "reader_threads": 2,
    "POSTS_PER_PAGE": 10,
    "basedir": basedir
}

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'  # TODO: Change for production deployment

OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]


engine = create_engine(configs["db_connector"],
                       convert_unicode=True)
                       # sqllite does not do pool size
                       # pool_size=configs.get("reader_threads"))

metadata = MetaData(bind=engine)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


Model = declarative_base()
Model.query = db_session.query_property()


# this needs to be done to properly register metadata!!!
# import database.models  # this is breaking on import db name... circ imports?
