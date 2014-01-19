# import os
# basedir = os.path.abspath(os.path.dirname(__file__))
#
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '../db/controller.db')
# SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
#
# ver = "0.0.0"
#
# configs = {
#
#     "User-Agent": "feed_getter.v{0}".format(ver),
#     "SQLALCHEMY_DATABASE_URI" : 'sqlite:///' + os.path.join(basedir, '../db/controller.db'),
#     "SQLALCHEMY_MIGRATE_REPO" : os.path.join(basedir, '../db/db_repository'),
#     "db_connector" : SQLALCHEMY_DATABASE_URI,
#     "reader_threads" : 2,
#     "POSTS_PER_PAGE" : 10
#
# }