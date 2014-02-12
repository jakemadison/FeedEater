# this module deals with adding, removing, updating user feeds.
# it will be called by front end actions
import FeedGetter
from feedeater.database.models import User, UserFeeds, Feed, Entry
from feedeater import db
# from feedeater.debugger import debugging_suite as ds
import getfeeds
import storefeeds
import parsenewfeed

db_session = db.session


def change_user_tags(user, entries):

    return {'taglist': 1}



def add_user_feed(user, feed):

    # check to see if this feed already exist in user table
    exists = db_session.query(Feed).filter_by(feed_url=feed).first()

    if exists:
        print "feed already exists in feed table"

        already_associated = db_session.query(UserFeeds).filter_by(feedid=exists.id).first()

        if already_associated:
            print "this feed is already associated with the current user, return error for info display"
            return "already_associated"

        else:
            # add this feed to user_feed table
            new_user_feed = UserFeeds(userid=user.id, feedid=exists.id, is_active=1)

            try:
                db_session.add(new_user_feed)
                db_session.commit()

            except Exception, e:
                print "error associating feed!"
                print str(e)
                db_session.rollback()
                return "error_adding_feed"

            else:
                return "success"

    # now comes the hard part... attempt to get a totally new feed:
    else:
        returned_url = parsenewfeed.parsefeed(feed)
        if returned_url:
            print "found valid rss"

            # add to feed table, add to userfeed table, get new entries.
            # later: add to cache?

            return "success"

        else:
            print "no valid url found at this address"
            return "no_feed_found"


def remove_user_feed(user, uf_id):
    print user
    print uf_id
    print "success!"

    remove = db_session.query(UserFeeds).filter_by(id=uf_id).first()

    if remove:
        try:
            db_session.delete(remove)
            db_session.commit()

        except Exception, e:
            print "error deleting feed", str(e)
            db_session.rollback()
            return "error_deleting_feed"

        else:
            return "successfully deleted"

    else:
        return "feed_id not found"


def get_guest_feeds():
    # qry = db_session.query(Feed)
    # qry.filter(Feed.id < 3)
    final_res = {'feed_data': [{'url': u'http://ancientpeoples.tumblr.com/rss',
                                'desc': u'A blog about everything in the Ancient World, run \
                                by history students and graduates from different fields.',
                                'title': u'Ancient Peoples'},
                               {'url': u'http://xkcd.com/rss.xml',
                                'desc': u'xkcd.com: A webcomic of romance and math humor.',
                                'title': u'xkcd.com'}],
                 'user_id': 1}

    return final_res


def get_user_feeds(user=None):

    feed_list = []
    #feed_data = {}
    final_list = []

    if user:
        qry = db_session.query(User, UserFeeds, Feed)
        qry = qry.filter(Feed.id == UserFeeds.feedid, UserFeeds.userid == User.id)

        for each in qry.filter(User.id == user.id).all():
            u_table, uf_table, f_table = each

            # add user_feed tag/category/star data here in dictionary:
            feed_data = {'title': f_table.title, 'url': f_table.feed_url,
                         'desc': f_table.description, 'active': uf_table.is_active,
                         'uf_id': uf_table.id, 'feed_id': uf_table.feedid}
            final_list.append(feed_data)

            feed_list.append(f_table.feed_url)  # is this actually being used at all??

        final_res = {'user_id': u_table.id, 'feed_data': final_list}

        print final_res

        return final_res

    else:
        feed_list = Feed.query.all()

    return [q.feed_url for q in feed_list]


# @ds.LogDebug
def get_user_entries(user):

    #this needs to return a query object so we can paginate results
    try:

        # query_result = Entry.query.order_by(Entry.published.desc())

        # qry = Entry.query.filter(Entry.feed_id == UserFeeds.feedid,
        #                  UserFeeds.userid == User.id,
        #                  UserFeeds.is_active == 1).order_by(Entry.published.desc())


        qry = Entry.query.order_by(Entry.published.desc())

        # qry = db_session.query(User, UserFeeds, Entry)
        # qry = qry.filter(Entry.feed_id == UserFeeds.feedid,
        #                  UserFeeds.userid == User.id,
        #                  UserFeeds.is_active == 1).order_by(Entry.published.desc())

    except Exception, e:
        print 'errrror with getting entries..'
        print str(e)

    else:
        print qry
        return qry


def update_is_active(ufid, active):

    try:
        db_session.query(UserFeeds).filter_by(id=ufid).update(
            {
                "is_active": active,
            })

        db_session.commit()

    except Exception, e:
        print 'errrror with existing is_active record'
        print str(e)
        db_session.rollback()


def update_users_feeds(u):

    # select title from feed f join userfeeds uf on f.id = uf.id

    try:
        user_record = db.session.query(User).filter(User.nickname == u.nickname).first()
        subs = db_session.query(UserFeeds).filter(UserFeeds.userid == user_record.id).all()

    except Exception, e:
        print 'DB error retrieving user feeds'
        print str(e)

    else:
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

    # get_user_entries(u)

#TODO: actually, might just be better to check most recent update and only look at those
# entries that are actually greater than that time, skipping the rest except for once per day
# check... hmmm

    xx = get_user_feeds(u)
    # send_feed = [f['url'] for f in x['feed_data']]  # expand to send both url and feed_id

    send_feed = []
    for f in xx['feed_data']:
        unit = {'feed_id': f['feed_id'], 'url': f['url']}
        send_feed.append(unit)
        # send_feed.append(f['url'])

    # result = []
    # for each in send_feed:
    #     result = getfeeds.feed_request(each)
    #     print result

    # print send_feed

    # for each in send_feed:
    #     result = getfeeds.feed_request(each)

    # for each in result['posts']:
    #     storefeeds.add_entry(result, update_entries=True)

    #print send_feed
    FeedGetter.main(send_feed)




