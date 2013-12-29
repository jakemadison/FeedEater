from app import Model
from sqlalchemy import Column, Integer, String, Text

ROLE_USER = 0
ROLE_ADMIN = 1


class Entry(Model):
    __tablename__ = "entry"
    id = Column('id', Integer, primary_key=True)
    feed_id = Column(Integer)
    published = Column(Integer)
    updated = Column(Integer)
    title = Column(String(1024))
    content = Column(Text)
    description = Column(String(256))
    link = Column(String(1024))
    remote_id = Column(String(1024))

    def __init__(self, feed_id=None, published=None, updated=None, title=None, content=None, description=None,
                 link=None, remote_id=None,):
        self.feed_id = feed_id
        self.published = published
        self.updated = updated
        self.title = title
        self.content = content
        self.description = description
        self.link = link
        self.remote_id = remote_id


class Feed(Model):
    __tablename__ = "feed"
    id = Column('id', Integer, primary_key=True)
    feed_url = Column(String(1024))
    last_checked = Column(Integer)
    subscribers = Column(Integer)
    title = Column(String(128))
    update_frequency = Column(Integer)
    favicon = Column(String(1024))
    metadata_update = Column(Integer)

    def __init__(self, update_frequency, favicon, feed_url=None, last_checked=1, subscribers=1, title=u"Some feed",
                 metadata_update=1):
        self.feed_url = feed_url
        self.last_checked = last_checked
        self.subscribers = subscribers
        self.title = title
        self.update_frequency = update_frequency
        self.favicon = favicon
        self.metadata_update = metadata_update
