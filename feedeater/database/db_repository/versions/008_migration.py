from sqlalchemy import *
from migrate import *


#from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
entry = Table('entry', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('feed_id', Integer),
    Column('published', Integer),
    Column('updated', Integer),
    Column('title', String),
    Column('content', Text),
    Column('description', String),
    Column('link', String),
    Column('remote_id', String),
)

feed = Table('feed', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('feed_url', String),
    Column('last_checked', Integer),
    Column('subscribers', Integer),
    Column('title', String),
    Column('update_frequency', Integer),
    Column('favicon', String),
    Column('metadata_update', Integer),
)

post = Table('post', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', String),
    Column('timestamp', DateTime),
    Column('user_id', Integer),
)

user = Table('user', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('nickname', String),
    Column('email', String),
    Column('role', SmallInteger),
    Column('password', String),
    Column('username', String),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['entry'].drop()
    pre_meta.tables['feed'].drop()
    pre_meta.tables['post'].drop()
    pre_meta.tables['user'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['entry'].create()
    pre_meta.tables['feed'].create()
    pre_meta.tables['post'].create()
    pre_meta.tables['user'].create()
