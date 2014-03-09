from sqlalchemy import Column, Integer, String, Text, SmallInteger, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import backref, relationship, query
# from datetime import datetime, timedelta
# import urlparse
from feedeater import db
from hashlib import md5

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

    def get_user_cat(self, userid):


        qry = UserFeeds.query.filter(UserFeeds.feedid == self.id, UserFeeds.userid == userid).first()

        if qry:
            return qry.category
        else:
            return "Uncategorized"

    def get_user_topics(self):
        pass

    def get_user_entry_records(self, user_id):
        qry = UserEntry.query.filter(UserEntry.entryid == self.id, UserEntry.userid == user_id)

        if qry.first() is None:
            return {"status": False, "record": UserEntry(entryid=self.id, userid=user_id)}

        else:
            return {"status": True, "query": qry.first()}



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

    def __init__(self, userid, feedid, is_active=True, category="None"):
        self.feedid = feedid
        self.userid = userid
        self.is_active = is_active
        self.category = category


class UserPrefs(Model):

    __tablename__ = "user_preferences"

    id = Column('id', Integer, primary_key=True)
    userid = Column(Integer, ForeignKey("user.id"))
    posts_per_page = Column(Integer, default=10)
    compressed_view = Column(Boolean, default=False)




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
    uprefs = relationship("UserPrefs", backref='users_pref')
    # posts = relationship('Post', backref = 'author', lazy = 'dynamic')

    def get_user(self, uid):
        qry = self.query.filter(self.id == uid).first()
        return qry


    def get_avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)


    def get_entries(self):

        # this needs to change to only get active entries
        # probably move this to user_feeds and do a join there.
        query_result = Entry.query.order_by(Entry.published.desc())
        return query_result

    def get_entries_new(self):

        print "----------------------------------------------running get entries new!!!"
        qry = Entry.query.filter(Entry.feed_id == UserFeeds.feedid,
                         UserFeeds.userid == self.id,
                         UserFeeds.is_active == 1).order_by(Entry.published.desc())



        # qry = query(Entry, UserEntry).outerjoin(UserEntry, Entry.id == UserEntry.entryid).filter(Entry.feed_id == UserFeeds.feedid,
        #                          UserFeeds.userid == User.id,
        #                          UserFeeds.is_active == 1).order_by(Entry.published.desc())

        print '----------------', qry.first()

        # print '_______________', dir(qry.first())


        return qry


    def get_userentries(self):

        qry = Entry.query.filter(UserFeeds.userid == self.id,  # get subscriptions associated with user
                                 Entry.feed_id == UserFeeds.feedid,  # only get entries that user subs to
                                 UserFeeds.is_active == 1  # get only active ones
                                 )
        #qry.outerjoin(UserEntry, Entry.id == UserEntry.entryid, User.id == UserEntry.userid)
        qry.join(UserFeeds, (UserFeeds.userid == User.id))
        qry.order_by(Entry.published.desc())
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
        return '<User %r>' % (self.username)


class UserEntry(Model):

    """list of user/entries, whether they are read/unread, starred/unstarred"""

    __tablename__ = "user_entry"

    id = Column(Integer, primary_key=True)
    entryid = Column(Integer, ForeignKey("entry.id"))
    userid = Column(Integer, ForeignKey("user.id"))
    starred = Column(Boolean, default=False)
    unread = Column(Boolean, default=True)

    entry = relationship("Entry", backref=backref("user_entries"))
    # user = relationship("user")

    def __init__(self, entryid, userid, starred=False, unread=True):
        self.entryid = entryid
        self.userid = userid
        self.starred = starred
        self.unread = unread


# for every user+entry combination, these are tags to apply:
class UserEntryTags(Model):

    """from list of all tags per user, apply tags to individual user/entries"""

    __tablename__ = "entry_tags"

    id = Column(Integer, primary_key=True)
    user_entry_id = Column(Integer, ForeignKey("user_entry.id"))
    tag = Column(String(64))
    # may want to put in back_refs here (and on entry, and user)

    def __init__(self):
        pass



print "done loading models.py!"