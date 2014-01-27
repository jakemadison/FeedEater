# this module deals with adding, removing, updating user feeds.
# it will be called by front end actions
import FeedGetter
from feedeater.database.models import User, UserFeeds, Feed
from feedeater import db

db_session = db.session


def add_user_feed():
    pass


def remove_user_feed():
    pass


def get_user_feeds(user=None):

    feed_list = []

    if user:
        # this needs work to retrieve properly... damn you sqlalchemy.
        sublist = UserFeeds.query.filter(UserFeeds.id == user.id).all()

    else:
        feed_list = Feed.query.all()

    return [q.feed_url for q in feed_list]



def update_users_feeds(u):

    # select title from feed f join userfeeds uf on f.id = uf.id



    try:
        user_record = db.session.query(User).filter(User.nickname == u.nickname).first()
        subs = db_session.query(UserFeeds).filter(UserFeeds.userid == user_record.id).all()

    except Exception, e:
        print 'DB error retrieving user feeds'
        print str(e)
        subs = None

    if subs:

        subs_list = [x.feedid for x in subs]

        print subs_list
        user_feeds = db_session.query(Feed).filter(Feed.id == subs_list).all()
        feed_list = [x.title for x in user_feeds]
        FeedGetter.main(feed_list)


def add_feed_category():
    pass


def remove_feed_category():
    pass


if __name__ == "__main__":
    u = User(nickname="jmadison", email="jmadison@quotemedia.com", role=0, id=1)
    x = get_user_feeds(u)

    print [e for e in x]
    FeedGetter.main(x)


