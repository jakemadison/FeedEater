# helper script to update unread counts following DB migration
from __future__ import print_function
import FeedGetter
from feedeater.database.models import User, UserFeeds, Feed, Entry, UserEntryTags, UserEntry, UserPrefs
from feedeater import db
from feedeater.config import configs as c
from feedeater.database import models
from sqlalchemy import or_

db_session = db.session


def calculate_unread_count(user_id, feed_id):

    entry_count = db_session.query(UserFeeds, Entry, UserEntry)
    entry_count = entry_count.join(Entry, Entry.feed_id == UserFeeds.feedid)
    entry_count = entry_count.filter(UserFeeds.userid == user_id, Entry.feed_id == feed_id)
    entry_count = entry_count.outerjoin(UserEntry, UserEntry.entryid == Entry.id)
    entry_count = entry_count.filter(or_(UserEntry.unread == True, UserEntry.unread == None))

    final_count = entry_count.count()

    return final_count


def update_unread_count(user_feed_id, u, count):

    print('update with count: {0}, user: {1}, feedid: {2}'.format(count, u, user_feed_id))

    if not count:
        count = 0

    db_session.query(UserFeeds).filter_by(feedid=user_feed_id, userid=u).update(
        {
            "unread_count": count
        })

    db_session.commit()

    current_count = db_session.query(UserFeeds.unread_count)
    current_count = current_count.filter(UserFeeds.userid == u, UserFeeds.feedid == user_feed_id).all()
    print(current_count)


def get_feed_id_list(u_id):

    feed_id_q = db_session.query(UserFeeds.id)
    feed_id_q = [uf_id[0] for uf_id in feed_id_q.filter(UserFeeds.userid == u_id).all()]

    return feed_id_q


if __name__ == "__main__":

    # get all users:
    user_id_list = [u_id[0] for u_id in db_session.query(User.id).all()]

    for user_id in user_id_list:
        print('processing feeds for user: {0}'.format(user_id))

        # get all feed ids for this user:
        feed_id_list = get_feed_id_list(user_id)

        # calculate unread counts for each feed:
        for feed_id in feed_id_list:
            unread_count = calculate_unread_count(user_id, feed_id)

            # update unread count for user
            update_unread_count(feed_id, user_id, unread_count)




    print('done!')