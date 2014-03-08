import FeedGetter
from feedeater.database.models import User, UserFeeds, Feed, Entry, UserEntryTags, UserEntry, UserPrefs, ROLE_USER
from feedeater import db
# from feedeater.debugger import debugging_suite as ds
import getfeeds
import storefeeds
import parsenewfeed
from feedeater.config import configs as c

db_session = db.session


def add_user(resp):
    nickname = resp.nickname
    if nickname is None or nickname == "":
        nickname = resp.email.split('@')[0]

    user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
    db.session.add(user)
    db.session.commit()

    user = db_session.query.filter(User.email == resp.email).first()
    prefs = UserPrefs({"userid": user.id})
    db_session.add(prefs)
    db_session.commit()
