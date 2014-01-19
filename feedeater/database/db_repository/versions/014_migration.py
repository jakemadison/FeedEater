from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
entry = Table('entry', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('feed_id', Integer),
    Column('published', Integer),
    Column('updated', Integer),
    Column('title', String(length=1024)),
    Column('content', Text),
    Column('description', String(length=256)),
    Column('link', String(length=1024)),
    Column('remote_id', String(length=1024)),
)

feed = Table('feed', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('feed_url', String(length=1024)),
    Column('last_checked', Integer),
    Column('subscribers', Integer),
    Column('title', String(length=128)),
    Column('update_frequency', Integer),
    Column('favicon', String(length=1024)),
    Column('metadata_update', Integer),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=64)),
    Column('nickname', String(length=64)),
    Column('email', String(length=120)),
    Column('role', SmallInteger, default=ColumnDefault(0)),
    Column('password', String(length=64)),
)

userfeeds = Table('userfeeds', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('userid', Integer),
    Column('feedid', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['entry'].create()
    post_meta.tables['feed'].create()
    post_meta.tables['user'].create()
    post_meta.tables['userfeeds'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['entry'].drop()
    post_meta.tables['feed'].drop()
    post_meta.tables['user'].drop()
    post_meta.tables['userfeeds'].drop()
