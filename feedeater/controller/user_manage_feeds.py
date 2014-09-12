import FeedGetter
from feedeater.database.models import User, UserFeeds, Feed, Entry, UserEntryTags, UserEntry, UserPrefs
from feedeater import db
import getfeeds
import storefeeds
import parsenewfeed
from feedeater.config import configs as c
from feedeater.display.views import custom_filters
from feedeater.database import models

db_session = db.session

import logging
from feedeater import setup_logger
logger = logging.getLogger(__name__)
setup_logger(logger)
logger.setLevel(logging.INFO)


#####
# Functions for reading subscription states:
#####

def get_unread_count(feed_id, user):

    """get the number of unread entries in the feed.  Currently only returning
       the total count of all entries in the feed."""

    logger.debug('getting unread count for feed: {0}, user_id: {1}'.format(feed_id, user.id))

    entry_count = db_session.query(Entry).filter(Entry.feed_id == feed_id).count()

    # to get an unread count, need count of total,
    # count of "read" and subtract.  remember, userEntry is only created on demand
    # so missing entries there should be assumed to be unread entries.

    # ORM this guy:
    # select count(*) from userfeeds uf join entry e on e.feed_id = uf.feedid
    # left join user_feed_entry ufe on ufe.entryid = e.id
    # where uf.userid = 3 and (ufe.unread = 1 or ufe.unread is null)

    logger.debug('count: {0}'.format(entry_count))
    return entry_count


#####
# Functions for recalculating entries:
#####
def _generate_calculation_query(user, only_star):
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

    # ah crap. does this need to be a left join on UserEntry?
    qry = db_session.query(User, UserFeeds, Feed, Entry, UserEntry)
    logger.debug('query done, filter/joining')

    qry = qry.filter(UserFeeds.userid == User.id)
    qry = qry.filter(Feed.id == UserFeeds.feedid)
    qry = qry.filter(Entry.feed_id == Feed.id)
    qry = qry.filter(User.id == user.id)
    # qry = qry.filter(UserFeeds.id.in_(active_list))
    qry = qry.filter(UserFeeds.is_active == True)
    qry = qry.outerjoin(UserEntry, UserEntry.entryid == Entry.id)

    if only_star:
        qry = qry.filter(UserEntry.starred == True)

    qry = qry.order_by(Entry.published.desc())

    return qry


def _generate_start_end_pos(page, p, n, current, per_page):
    if current:
        # determine main page start and end and set pager_indicator accordingly,
        # assuming we are generating entries for the main page
        start_pos = ((page-1)*per_page)
        end_pos = start_pos + per_page

        logger.debug('start_pos {0}, end_pos{1}'.format(start_pos, end_pos))

    return start_pos, end_pos


def _set_pager_indicator(pager_indicator, start, end, count):

    if start == 0:
        pager_indicator["has_prev"] = False
    else:
        pager_indicator["has_prev"] = True

    if count > end:
        pager_indicator["has_next"] = True
    else:
        pager_indicator["has_next"] = False

    return pager_indicator


def _generate_entry_list(qry, start, end):
    final_list = []

    for index, each in enumerate(qry[start:end]):

        u_table, uf_table, f_table, e_table, ufe_table = each

        if ufe_table is None:
            ufe = {'id': None, 'unread': True, 'starred': False}
        else:
            ufe = {'id': ufe_table.id, 'unread': ufe_table.unread, 'starred': ufe_table.starred}

        #okay, hooked into the custom filters:
        pub_time = custom_filters.parse_time(e_table.published)
        pub_title = custom_filters.truncate_title(e_table.title)
        pub_link = custom_filters.url_base(f_table.feed_url)

        entry_data = {'title': f_table.title, 'url': pub_link,
                      'desc': f_table.description, 'active': uf_table.is_active,
                      'uf_id': uf_table.id, 'feed_id': uf_table.feedid,
                      'entry_id': e_table.id,
                      'category': uf_table.category,
                      'entry_title': pub_title,
                      'entry_content': e_table.content,
                      'entry_published': pub_time,
                      'entry_link': e_table.link,
                      'user_entry_id': ufe.get('id'),
                      'entry_unread': ufe.get('unread'),
                      'entry_starred': ufe.get('starred')}

        final_list.append(entry_data)

    return final_list


def recalculate_entries(user, page_id, only_star=False, p=False, n=False, current=True):

    """given a user and page (optionally, starred only) recalculate the entries to be displayed.
       It would be worth having this look forward/backward an extra page to speed up page-change,
       since this is an expensive function."""

    # this function should really only take no. entries, and offset, and return that
    # the front end should be dealing with how it wants to work with the data that's returned
    # including what do do with the pager indicator.
    # i guess it needs to also send back the count of total entries, to determine pager has_next

    # init stuff:
    per_page = int(c['POSTS_PER_PAGE'])
    page = int(page_id)
    logger.debug('----> current page: {0} ----> posts per page: {1}'.format(page, per_page))
    pager_indicator = {"has_prev": None, "has_next": None}

    #put together our query object:
    qry = _generate_calculation_query(user, only_star)

    total_records = qry.count()
    logger.debug("count of records :  {0}".format(total_records))

    # determine our start and end positions of entries:
    start_pos, end_pos = _generate_start_end_pos(page, p, n, current, per_page)

    # if we're getting the current page, figure out our pager indicators:
    if current:
        pager_indicator = _set_pager_indicator(pager_indicator, start_pos, end_pos, total_records)

    ###
    # finally, put together out final list of entries, and return to view:
    final_list = _generate_entry_list(qry, start_pos, end_pos)

    return final_list, pager_indicator, total_records, per_page


def get_progress():

    """get the current progress of feeds refresh.  returns the list of
       feeds (feed_ids) which have finished updating"""

    return FeedGetter.fin_q


def get_user_feeds(user=None):

    """get all feeds the user is subscribed to"""

    feed_list = []

    final_list = []
    cat_list = []
    u_table, uf_table, f_table = (None, None, None)

    if user:
        qry = db_session.query(User, UserFeeds, Feed)
        qry = qry.filter(Feed.id == UserFeeds.feedid, UserFeeds.userid == User.id)

        for each in qry.filter(User.id == user.id).all():
            u_table, uf_table, f_table = each

            unread_count = get_unread_count(uf_table.feedid, user)

            # add user_feed tag/category/star data here in dictionary:
            feed_data = {'title': f_table.title, 'url': f_table.feed_url,
                         'desc': f_table.description, 'active': uf_table.is_active,
                         'uf_id': uf_table.id, 'feed_id': uf_table.feedid,
                         'category': uf_table.category, 'count': unread_count}
            final_list.append(feed_data)

            cat_list.append(uf_table.category)
            feed_list.append(f_table.feed_url)  # is this actually being used at all??

        cat_list = set(cat_list)

        if not uf_table:
            pass

        final_res = {'user_id': user.id, 'feed_data': final_list, 'cat_list': cat_list}

        return final_res

    else:
        feed_list = Feed.query.all()

    return [q.feed_url for q in feed_list]


def get_user_prefs(user):

    """get user feed preferences. Currently only compressed vs uncompressed view"""

    prefs = db_session.query(UserPrefs).filter_by(userid=user.id)
    x = prefs.first()

    if x is None:
        new_prefs = models.UserPrefs(userid=user.id)
        db_session.add(new_prefs)
        db_session.commit()
        c_view = 0

    else:
        c_view = x.compressed_view

    return c_view


#####
# Functions for adding/removing subscriptions:
#####

def add_user_feed(user, feed):

    """add a new feed to a user's subscription list.  Check to see if we already have
       the feed and its entries (because of another user, possible).  Otherwise,
       go get everything for the feed."""

    def associate_feed_with_user():

        new_user_feed = UserFeeds(userid=user.id, feedid=exists.id, is_active=1)

        try:
            db_session.add(new_user_feed)
            db_session.commit()

        except Exception, e:
            logger.exception("error associating feed! rolling back DB")
            db_session.rollback()

            return {'message': "error_adding_feed", 'data': False}

        else:
            # we should probably go get entries for that new feed here...
            return {'message': "success", 'data': False}

    # first get the actual feed from user's input: maybe it's worth checking if exists first before going
    # through the hassle of feedfinder... meh, whatever.
    returned_feed, feeds_len = parsenewfeed.parsefeed(feed)

    if returned_feed:
        returned_feed = [str(r) for r in returned_feed]

        if feeds_len > 1:
            return {'message': 'multiple_feeds_found', 'data': returned_feed}

        logger.info("found valid rss: {0}".format(returned_feed))
        returned_feed = returned_feed[0]

    else:
        logger.warn('no feed found for that url')
        return {'message': 'no_feed_found', 'data': False}

    # check to see if this feed already exist in user table
    exists = db_session.query(Feed).filter_by(feed_url=returned_feed).first()

    if exists:
        logger.info("feed already exists in feed table")
        already_associated = db_session.query(UserFeeds).filter_by(feedid=exists.id, userid=user.id).first()

        if already_associated:
            logger.info("this feed is already associated with the current user: {0}".format(user.nickname))
            return {'message': "already_associated", 'data': False}

        else:
            # add this feed to user_feed table
            result = associate_feed_with_user()
            # should probably update entries after adding...
            return {'message': result, 'data': False}

    else:
        logger.info("totally new feed, adding everything")

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

        return {'message': "success", 'data': False}


def remove_user_feed(user, uf_id):

    """remove a user's feed from their subscriptions list.
       keep the feed and entries, as other users might be subscribed too"""

    logger.debug('removing feed for {0}, ufid = {1}'.format(user, uf_id))

    remove = db_session.query(UserFeeds).filter_by(id=uf_id).first()

    if remove:
        try:
            db_session.delete(remove)
            db_session.commit()

        except Exception, e:
            logger.exception("error deleting feed.  rolling back DB")
            db_session.rollback()
            return "error_deleting_feed"

        else:
            return "successfully deleted"

    else:
        return "feed_id not found"


#####
# Functions for changing subscription attributes:
#####

def apply_feed_category(category, ufid, remove=False):

    """set/change a feed's category"""

    logger.debug('category: {0}'.format(category))

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


#####
# Functions for changing subscriptions displayed:
#####

def single_active(user, ufid):

    """turn on a single feed, turn off all other feeds"""

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
        logger.exception('errrror with existing is_active record. rolling back DB')
        db_session.rollback()


def all_active(user):

    """turn on all feeds"""

    try:
        db_session.query(UserFeeds).filter_by(userid=user.id).update(
            {
                "is_active": True
            })

        db_session.commit()

    except Exception, e:
        logger.exception('errrror with existing is_active record. rolling back DB')
        db_session.rollback()


def toggle_category(user, cat):

    """turn an entire category on if any single feed in that category is set to off
       if all feeds in that category are on, turn the whole category off"""

    try:
        qry = db_session.query(UserFeeds).filter_by(userid=user.id, category=cat)
        existing = qry.all()

        # check if any are False, if so: set all to true, otherwise, set all to False.
        if any([x.is_active is False for x in existing]):
            qry.update({"is_active": True})
            all_on = True
        else:
            qry.update({"is_active": False})
            all_on = False

        db_session.commit()
        return all_on

    except Exception, e:
        logger.exception('errrror with existing is_active record. rolling back db')
        db_session.rollback()


def update_is_active(uf_id):

    """switch between active and inactive for a single feed"""

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
        logger.exception('errrror with existing is_active record. rolling back db')
        db_session.rollback()


#####
# Main Function:
#####

def main(user):
    xx = get_user_feeds(user)
    send_feed = []

    logger.debug('xx: {0}'.format(xx))

    for f in xx['feed_data']:
        unit = {'feed_id': f['feed_id'], 'url': f['url']}
        send_feed.append(unit)

    FeedGetter.main(send_feed)


if __name__ == "__main__":
    u = User(nickname="jmadison", email="jmadison@quotemedia.com", role=0, id=1)
    main(u)

