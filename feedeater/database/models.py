from sqlalchemy import Column, Integer, String, Text, SmallInteger, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import backref, relationship
from datetime import datetime, timedelta
import urlparse
from feedeater import db

Model = db.Model

ROLE_USER = 0
ROLE_ADMIN = 1


print "models imported as", __name__


## Macro Level Data:
# all entries for all subscribed feeds
class Entry(Model):

    __tablename__ = "entry"

    id = Column('id', Integer, primary_key=True)
    feed_id = Column(Integer, ForeignKey("feed.id"))
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

    def json_entry(self):
        result = {"id": self.id, "feed_id": self.feed_id, "published": self.published,
                  "updated": self.updated, "title": self.title, "content": self.content,
                  "description": self.description, "link": self.link, "remote_id": self.remote_id}
        return result

    # TODO: These probably make more sense in a controller_util.py file.
    # they are more application logic than model logic, no?

    # people don't like reading unix timestamps
    # use weekdays unless older than one week.
    def get_parsed_time(self):
        parse_date = datetime.fromtimestamp(self.published)
        now = datetime.now()
        starter_word = ''

        if parse_date >= now - timedelta(days=7):  # this week?
            if parse_date >= now - timedelta(days=1):  # yesterday? (this checks for within 24hours.
                                                        # need > midnight
                starter_word = ''
                form = '%I:%M%p'

            else:
                form = '%a %I:%M%p'

        else:
            form = '%I:%M%p %m/%d/%Y'

        return starter_word + parse_date.strftime(form).lstrip('0')

    # quick method to return truncated (at the space) titles
    def get_title(self):
        title = self.title

        if not title:
            title = 'no title'  # not needed.

        if len(title) > 50:
            temp_t = title[0:50]
            k = temp_t.rfind(" ")
            if k:
                short_title = temp_t[:k]+"..."
                return short_title
            else:
                short_title = temp_t[:47]+"..."
                return short_title

        return title

    def get_feed_base(self):
        return urlparse.urlparse(self.remote_id).netloc.lstrip('www.')


# list of active feeds from all active subscribers
class Feed(Model):
    __tablename__ = "feed"

    id = Column('id', Integer, primary_key=True)
    feed_url = Column(String(1024))
    feed_site = Column(String(1024))
    description = Column(String(1024))
    last_checked = Column(Integer)
    subscribers = Column(Integer)
    title = Column(String(128))
    update_frequency = Column(Integer)
    favicon = Column(String(1024))
    metadata_update = Column(Integer)
    ufeeds = relationship("UserFeeds", backref="source")
    entries = relationship("Entry", backref="entry_source")

    def __init__(self, update_frequency='0', favicon=None, feed_url=None, feed_site=None,
                 last_checked=1,
                 subscribers=1, title=u"Some feed",
                 metadata_update=1, description=None):

        self.feed_url = feed_url
        self.feed_site = feed_site
        self.description = description
        self.last_checked = last_checked
        self.subscribers = subscribers
        self.title = title
        self.update_frequency = update_frequency
        self.favicon = favicon
        self.metadata_update = metadata_update


## User Level Data:
# associate users with feeds they are subscribed to:
# also put in here, feed-related tags
class UserFeeds(Model):

    __tablename__ = "userfeeds"

    id = Column('id', Integer, primary_key=True)
    userid = Column(Integer, ForeignKey("user.id"))
    feedid = Column(Integer, ForeignKey("feed.id"))
    is_active = Column(Boolean, default=True)
    category = Column(String(64))

    def __init__(self, userid, feedid, is_active=True, category=None):
        self.feedid = feedid
        self.userid = userid
        self.is_active = is_active
        self.category = category


# all user accounts registered with the controller
class User(Model):

    __tablename__ = "user"

    id = Column('id', Integer, primary_key=True)
    username = Column(String(64), unique=True)
    nickname = Column(String(64), unique=True)
    email = Column(String(120), unique=True)
    role = Column(SmallInteger, default=ROLE_USER)
    password = Column(String(64), unique=True)
    ufeeds = relationship("UserFeeds")
    # posts = relationship('Post', backref = 'author', lazy = 'dynamic')

    def get_entries(self):

        # this needs to change to only get active entries
        # probably move this to user_feeds and do a join there.
        query_result = Entry.query.order_by(Entry.published.desc())
        return query_result

    def get_entries_new(self):

        qry = Entry.query.filter(Entry.feed_id == UserFeeds.feedid,
                         UserFeeds.userid == User.id,
                         UserFeeds.is_active == 1).order_by(Entry.published.desc())

        return qry


    # following are required by Flask-Login:
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class UserEntry(Model):

    """list of user/entries, whether they are read/unread, starred/unstarred"""

    __tablename__ = "userentrytags"

    id = Column(Integer, primary_key=True)
    entryid = Column(Integer, ForeignKey("entry.id"))
    userid = Column(Integer, ForeignKey("user.id"))
    starred = Column(Boolean, default=False)
    unread = Column(Boolean, default=True)

    def __init__(self, entryid, userid, topicid, starred=False, unread=True):
        self.entryid = entryid
        self.userid = userid
        self.starred = starred
        self.unread = unread


# for every user+entry combination, these are tags to apply:
class UserEntryTags(Model):

    """from list of all tags per user, apply tags to individual user/entries"""

    __tablename__ = "entrytags"

    id = Column(Integer, primary_key=True)
    userentryid = Column(Integer, ForeignKey("userentrytags.id"))
    tagid = Column(Integer, ForeignKey("usertags.id"))
    # may want to put in back_refs here (and on entry, and user)

    def __init__(self):
        pass


class UserTags(Model):

    """list of all tags per user"""

    __tablename__ = "usertags"

    id = Column(Integer, primary_key=True)
    tag = Column(String(64))

    def __init__(self, tag):
        self.tag = tag


print "done!"