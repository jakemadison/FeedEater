from feedeater.database.models import User, ROLE_USER  # ,UserFeeds, Feed, Entry, UserEntryTags, UserEntry, UserPrefs
from feedeater import db
# from feedeater.debugger import debugging_suite as ds
#import getfeeds
#import storefeeds
#import parsenewfeed
#from feedeater.config import configs as c
#import FeedGetter

db_session = db.session


def add_user(resp):

    # some auths contain a nick, some don't.
    # if they don't, use first segment of email:
    nickname = resp.nickname
    if nickname is None or nickname == "":
        nickname = resp.email.split('@')[0]

    user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
    db.session.add(user)
    db.session.commit()



    # preferences now has a check which will create the pref record
    # when required.  So i think I can just comment this out..
    # Ah, this is why the other bug:
    # user = db_session.query.filter(User.email == resp.email).first()
    # prefs = UserPrefs({"userid": user.id})
    # db_session.add(prefs)
    # db_session.commit()
