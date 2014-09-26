from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
entrytags = Table('entrytags', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('userentryid', Integer),
    Column('topic', String(length=64)),
)

userentries = Table('userentries', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['entrytags'].create()
    post_meta.tables['userentries'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['entrytags'].drop()
    post_meta.tables['userentries'].drop()
