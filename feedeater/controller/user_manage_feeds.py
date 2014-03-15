# this module deals with adding, removing, updating user feeds.
# it will be called by front end actions
import FeedGetter
from feedeater.database.models import User, UserFeeds, Feed, Entry, UserEntryTags, UserEntry, UserPrefs
from feedeater import db
# from feedeater.debugger import debugging_suite as ds
import getfeeds
import storefeeds
import parsenewfeed
from feedeater.config import configs as c

db_session = db.session


def recalculate_entries(active_list, user, p):

    feed_list = []
    #feed_data = {}
    final_list = []
    cat_list = []

    per_page = int(c['POSTS_PER_PAGE'])
    page = int(p)

    print '----> current page:', page, '----> posts per page:', per_page

    start_pos = ((page-1)*per_page)
    end_pos = start_pos + per_page

    print start_pos, end_pos


    print active_list, user

    # get all feed entries for user where UserFeeds.id in active_list
    # okay, so really this should be the only query used everywhere
    # and then we should pull things like "cat list" out of this giant, ugly thing
    # ^ that actually doesn't make sense, because if we only return the first page of results
    # we might not get all categories that we want in the sidebar.  we need a more "global" search for that
    # so they do need to be separate.  But, we can still do this for entry content.


    # god damn, that's some ugly SQL.. I could see a 5 table join having performance implications...

    # Okay, so really, this should just send entries, and there should be a separate GET request
    # that retrieves tag info, star info, etc etc etc.

    #

    # qry = db_session.query(User, UserFeeds, Feed, Entry, UserEntry)
    #
    # qry = qry.filter(Entry.feed_id == Feed.id, Feed.id == UserFeeds.feedid,
    #                  UserEntry.userfeedid == UserFeeds.id,
    #                  UserFeeds.userid == User.id, User.id == user.id, UserFeeds.id.in_(active_list))
    #

    qry = db_session.query(User, UserFeeds, Feed, Entry, UserEntry)

    qry = qry.filter(Entry.id == UserEntry.entryid, UserEntry.userfeedid == UserFeeds.id,
                     UserFeeds.userid == User.id, User.id == user.id, Feed.id == Entry.feed_id,
                     UserFeeds.id.in_(active_list))

    qry = qry.order_by(Entry.published.desc())

    for each in qry[start_pos:end_pos]:
        u_table, uf_table, f_table, e_table, ufe_table = each

        entry_data = {'title': f_table.title, 'url': f_table.feed_url,
                      'desc': f_table.description, 'active': uf_table.is_active,
                      'uf_id': uf_table.id, 'feed_id': uf_table.feedid,
                      'entry_id': e_table.id,
                      'category': uf_table.category,
                      'entry_title': e_table.title,
                      'entry_content': e_table.content,
                      'entry_published': e_table.published,
                      'entry_link': e_table.link,
                      'entry_starred': ufe_table.starred,
                      'entry_unread': ufe_table.unread}

        final_list.append(entry_data)

    for each in final_list:
        for k, v in each.iteritems():
            # print k, '---', v
            pass
        print '-----------'

    return final_list


def change_user_tags(user, entries):

    return {'taglist': 1}


def change_star_state(user, entryid):

    # this function is a boolean.. so it shouldn't care what the state originally was
    # it can be state agnostic.  same with the front end.  it only needs to know if
    # toggle at the back was successful or not
    current_state = db_session.query(UserEntry).filter(UserFeeds.userid == user.id,
                                                       UserEntry.entryid == entryid,
                                                       UserEntry.userfeedid == UserFeeds.id).first()

    qry = db_session.query(UserEntry).filter(UserEntry.id == current_state.id)

    # this should actually check if it exists, and add record if not.
    # which is a higher function that should be shared with change/add user tags

    # my entire model here for stars is bogus.  Tags and stars probably need to be separate tables
    # sigh.. one entry can have many tags per client, but each entry can only have a single star state (per client)
    if current_state:
        print "yes"
        if current_state.starred:

            print "was", current_state.starred

            qry.update({"starred": False})
            db_session.commit()

        else:
            print current_state.starred
            qry.update({"starred": True})
            db_session.commit()

        return True

    else:
        return False


def add_user_feed(user, feed):

    def associate_feed_with_user():

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
            # we should probably go get entries for that new feed here...
            return "success"

    # first get the actual feed from user's input: maybe it's worth checking if exists first before going
    # through the hassle of feedfinder... meh, whatever.
    returned_feed = parsenewfeed.parsefeed(feed)
    if returned_feed:
        print "found valid rss", returned_feed
    else:
        return 'no_feed_found'

    # check to see if this feed already exist in user table
    exists = db_session.query(Feed).filter_by(feed_url=returned_feed).first()

    if exists:
        print "feed already exists in feed table"
        already_associated = db_session.query(UserFeeds).filter_by(feedid=exists.id).first()

        if already_associated:
            print "this feed is already associated with the current user, return error for info display"
            return "already_associated"

        else:
            # add this feed to user_feed table
            result = associate_feed_with_user()
            # should probably update entries after adding...
            return result

    else:
        print "totally new feed, adding everything"

        get_result = getfeeds.get_feed_meta(returned_feed)
        print get_result
        storefeeds.store_feed_data(get_result)
        exists = db_session.query(Feed).filter_by(feed_url=returned_feed).first()
        associate_feed_with_user()
        f_obj = {'url': returned_feed, 'feed_id': exists.id}
        get_entries_res = getfeeds.feed_request(f_obj)
        storefeeds.add_entry(get_entries_res)
        # to add a new feed, we need to what...
        # attempt to actually fetch the feed?
        # ugh, this is actually running parsefeed twice.. one to check for existence
        # then one to actually add to the feed table..

        # add to feed table, add to userfeed table, get new entries.
        # later: add to cache?

        return "success"


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
    cat_list = []
    u_table, uf_table, f_table = (None, None, None)

    if user:
        qry = db_session.query(User, UserFeeds, Feed)
        qry = qry.filter(Feed.id == UserFeeds.feedid, UserFeeds.userid == User.id)

        for each in qry.filter(User.id == user.id).all():
            u_table, uf_table, f_table = each

            # add user_feed tag/category/star data here in dictionary:
            feed_data = {'title': f_table.title, 'url': f_table.feed_url,
                         'desc': f_table.description, 'active': uf_table.is_active,
                         'uf_id': uf_table.id, 'feed_id': uf_table.feedid,
                         'category': uf_table.category}
            final_list.append(feed_data)
            cat_list.append(uf_table.category)

            feed_list.append(f_table.feed_url)  # is this actually being used at all??

        cat_list = set(cat_list)

        if not uf_table:
            pass


        final_res = {'user_id': user.id, 'feed_data': final_list, 'cat_list': cat_list}

        # print final_res

        return final_res

    else:
        feed_list = Feed.query.all()

    return [q.feed_url for q in feed_list]


def test_get_entires(user):
    qry = db_session.query(User, UserFeeds, Entry, UserEntry)
    qry.filter(Entry.feed_id == UserFeeds.feedid,
                         UserFeeds.userid == user.id,
                         UserEntry.userid == user.id, UserEntry.entryid == Entry.id,
                         UserFeeds.is_active == 1).order_by(Entry.published.desc())
    return qry


def get_user_entry_records(user, entry_list):

    entry_records = []

    for each in entry_list.items:
        result = each.get_user_entry_records(user.id)

        if result["status"]:
            entry_records.append(result["query"])

        else:
            try:
                db_session.add(result["record"])

            except Exception, e:
                print str(e)

            else:
                db_session.commit()
                entry_records.append(result["record"])

    print "these are the recorddddds: ", entry_records


    # qry = UserEntry.query.filter(UserEntry.entryid == entry_list.id)




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


def single_active(user, ufid):

    try:
        db_session.query(UserFeeds).filter_by(userid=user.id).update(
            {
                "is_active": False
            })

        db_session.query(UserFeeds).filter_by(id=ufid).update(
            {
                "is_active": True
            })

        db_session.commit()

    except Exception, e:
        print 'errrror with existing is_active record'
        print str(e)
        db_session.rollback()


def all_active(user):

    try:
        db_session.query(UserFeeds).filter_by(userid=user.id).update(
            {
                "is_active": True
            })

        db_session.commit()

    except Exception, e:
        print 'errrror with existing is_active record'
        print str(e)
        db_session.rollback()


def activate_category(user, cat):

    try:
        db_session.query(UserFeeds).filter_by(userid=user.id).update(
            {
                "is_active": False
            })

        db_session.query(UserFeeds).filter_by(category=cat).update(
            {
                "is_active": True
            })

        db_session.commit()

    except Exception, e:
        print 'errrror with existing is_active record'
        print str(e)
        db_session.rollback()


def update_is_active(uf_id):
    try:
        print uf_id
        existing = db_session.query(UserFeeds).filter_by(id=uf_id).first()

        if existing.is_active == True:
            active = False

        elif existing.is_active == False:
            active = True


        db_session.query(UserFeeds).filter_by(id=uf_id).update(
            {
                "is_active": active
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


def apply_feed_category(category, ufid, remove=False):

    print category

    if remove:
        return False  # remove category for user/feed combination

    # otherwise, apply category to feedid for user
    try:
        active_row = db_session.query(UserFeeds).filter_by(id=ufid)
        active_row.update({"category": category})
        db_session.commit()

    except Exception, e:
        return "failed", str(e)

    else:
        return "success"


def get_user_prefs(user):

    prefs = db_session.query(UserPrefs).filter_by(userid=user.id)
    x = prefs.first()

    return x.compressed_view



def changeview(user):

    print 'changeview activated!'
    print "attempting to change view state for user: ", user.nickname, "id: ", user.id

    current_state = db_session.query(UserPrefs).filter_by(userid=user.id).first()

    if current_state.compressed_view:
        db_session.query(UserPrefs).filter_by(userid=user.id).update({"compressed_view": False})

    else:
        db_session.query(UserPrefs).filter_by(userid=user.id).update({"compressed_view": True})

    db_session.commit()

    return




def get_user_categories(user):
    # categories = db_session.query(UserFeeds).filter_by(userid=user.id)
    pass



def main(user):
    xx = get_user_feeds(user)
    send_feed = []

    for f in xx['feed_data']:
        unit = {'feed_id': f['feed_id'], 'url': f['url']}
        send_feed.append(unit)

    FeedGetter.main(send_feed)


if __name__ == "__main__":
    u = User(nickname="jmadison", email="jmadison@quotemedia.com", role=0, id=1)
    main(u)
    # get_user_entries(u)

#TODO: actually, might just be better to check most recent update and only look at those
# entries that are actually greater than that time, skipping the rest except for once per day
# check... hmmm

    # use this to update feeds for now:



    # apply_feed_category(u, "Cats", 4)
    # apply_feed_category(u, "Pics", 1)
    # apply_feed_category(u, "Pics", 5)
    # apply_feed_category(u, "Programming", 7)
    # apply_feed_category(u, "Programming", 6)
    #apply_feed_category(u, None, 3)


    # some feeds to add:
    # https://explosm.net/comics/3489/
    # http://theoatmeal.com/
    #