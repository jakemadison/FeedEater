#from app import Model
#from sqlalchemy import Column, Integer, String, Text, SmallInteger, DateTime, ForeignKey
from datetime import datetime, timedelta
import urlparse
from display import db

ROLE_USER = 0
ROLE_ADMIN = 1

# Model = db.Model

print "models imported as", __name__

class Entry(db.Model):
    __tablename__ = "entry"

    id = db.Column('id', db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer)
    published = db.Column(db.Integer)
    updated = db.Column(db.Integer)
    title = db.Column(db.String(1024))
    content = db.Column(db.Text)
    description = db.Column(db.String(256))
    link = db.Column(db.String(1024))
    remote_id = db.Column(db.String(1024))

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
                title = temp_t[:k]+"..."
            else:
                title = temp_t[:47]+"..."

        return title

    def get_feed_base(self):
        return urlparse.urlparse(self.remote_id).netloc




class Feed(db.Model):
    __tablename__ = "feed"

    id = db.Column('id', db.Integer, primary_key=True)
    feed_url = db.Column(db.String(1024))
    last_checked = db.Column(db.Integer)
    subscribers = db.Column(db.Integer)
    title = db.Column(db.String(128))
    update_frequency = db.Column(db.Integer)
    favicon = db.Column(db.String(1024))
    metadata_update = db.Column(db.Integer)

    def __init__(self, update_frequency, favicon, feed_url=None, last_checked=1, subscribers=1, title=u"Some feed",
                 metadata_update=1):
        self.feed_url = feed_url
        self.last_checked = last_checked
        self.subscribers = subscribers
        self.title = title
        self.update_frequency = update_frequency
        self.favicon = favicon
        self.metadata_update = metadata_update


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    nickname = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    password = db.Column(db.String(64), unique=True)
    # posts = relationship('Post', backref = 'author', lazy = 'dynamic')

    def get_entries(self):
        return Entry.query.order_by(Entry.published.desc())

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


# class Post(Model):
#     __tablename__ = "post"
#     id = Column(Integer, primary_key = True)
#     body = Column(String(140))
#     timestamp = Column(DateTime)
#     user_id = Column(Integer, ForeignKey('user.id'))
#
#     def __repr__(self):
#         return '<Post %r>' % (self.body)