#!../../../feed_env/bin/python

import imp
from migrate.versioning import api

from feedeater.config import configs
from feedeater import db

REPO = configs.get('SQLALCHEMY_MIGRATE_REPO')
URI = configs.get('SQLALCHEMY_DATABASE_URI')


migration = REPO + '/versions/%03d_migration.py' % (api.db_version(URI, REPO) + 1)
tmp_module = imp.new_module('old_model')
old_model = api.create_model(URI, REPO)

exec old_model in tmp_module.__dict__

script = api.make_update_script_for_model(URI, REPO, tmp_module.meta, db.metadata)
open(migration, "wt").write(script)
api.upgrade(URI, REPO)

print 'New migration saved as ' + migration
print 'Current database version: ' + str(api.db_version(URI, REPO))