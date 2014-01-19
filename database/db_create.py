#!../feedgetter_env/bin/python

import os.path
from migrate.versioning import api
from config import configs

REPO = configs.get('SQLALCHEMY_MIGRATE_REPO')
URI = configs.get('SQLALCHEMY_DATABASE_URI')

from config import Model, engine  # TODO model reference here

Model.metadata.create_all(bind=engine)


if not os.path.exists(REPO):
    api.create(REPO, 'database repository')
    api.version_control(URI, REPO)
else:
    api.version_control(URI, REPO, api.version(REPO))