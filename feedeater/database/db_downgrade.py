#!../feedgetter_env/bin/python
from migrate.versioning import api
from feedeater.config import configs

REPO = configs.get('SQLALCHEMY_MIGRATE_REPO')
URI = configs.get('SQLALCHEMY_DATABASE_URI')


v = api.db_version(URI, REPO)
api.downgrade(URI, REPO, v - 1)
print 'Current database version: ' + str(api.db_version(URI, REPO))