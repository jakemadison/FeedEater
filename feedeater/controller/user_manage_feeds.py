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



def get_guest_feeds():
    # qry = db_session.query(Feed)
    # qry.filter(Feed.id < 3)
    final_res = {'feed_data': [{'url': u'http://ancientpeoples.tumblr.com/rss',
                                'desc': u'A blog about everything in the Ancient World, run by history students and graduates from different fields.',
                                'title': u'Ancient Peoples'},
                               {'url': u'http://xkcd.com/rss.xml',
                                'desc': u'xkcd.com: A webcomic of romance and math humor.',
                                'title': u'xkcd.com'}],
                 'user_id': 1}

    return final_res


def get_user_feeds(user=None):

    feed_list = []
    feed_data = {}
    final_list = []

    if user:
        qry = db_session.query(User, UserFeeds, Feed)
        qry = qry.filter(Feed.id == UserFeeds.feedid, UserFeeds.userid == User.id)

        for each in qry.filter(User.id == user.id).all():
            u_table, uf_table, f_table = each

            # print u_table.id, u_table.nickname, ': ', f_table.feed_url, f_table.title, f_table.description

            feed_data = {'title': f_table.title, 'url': f_table.feed_url, 'desc': f_table.description}
            final_list.append(feed_data)

            # add user_feed tag/category/star data here in dicitionary.

            feed_list.append(f_table.feed_url)

        final_res = {'user_id': u_table.id, 'feed_data': final_list}

        print final_res

        return final_res




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
    send_feed = [f['url'] for f in x['feed_data']]
    FeedGetter.main(send_feed)




