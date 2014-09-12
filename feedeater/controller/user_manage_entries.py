from feedeater.database.models import UserFeeds, Entry, UserEntry, UserPrefs
from feedeater import db

db_session = db.session

import logging
from feedeater import setup_logger
logger = logging.getLogger(__name__)
setup_logger(logger, logging.DEBUG)


def mark_entry_read(entryid, userid):

    """ check for existence of user_feed_entry for user/entryid combo
     if exists, make unread = False
     if doesn't exist, make new record with unread=False"""

    logger.info('marking as read, entryid: {0}, userid: {1}'.format(entryid, userid))

    current_state = db_session.query(UserEntry).filter(UserFeeds.userid == userid,
                                                   UserEntry.entryid == entryid,
                                                   UserEntry.userfeedid == UserFeeds.id).first()

    if current_state is None:
        logger.debug("no userEntry found, adding a new one...")

        entry = db_session.query(Entry).filter(Entry.id == entryid).first()
        uf_id = db_session.query(UserFeeds).filter(UserFeeds.userid == userid,
                                                   UserFeeds.feedid == entry.feed_id).first().id

        new_user_entry = UserEntry(entryid, userid, userfeedid=uf_id, starred=False, unread=False)
        db_session.add(new_user_entry)
        db_session.commit()
        return True

    logger.debug('does exist, updating')
    qry = db_session.query(UserEntry).filter(UserEntry.id == current_state.id)

    qry.update({"unread": False})
    db_session.commit()

    return


def change_star_state(user, entryid):

    # this function is a boolean.. so it shouldn't care what the state originally was
    # it can be state agnostic.  same with the front end.  it only needs to know if
    # toggle at the back was successful or not
    current_state = db_session.query(UserEntry).filter(UserFeeds.userid == user.id,
                                                       UserEntry.entryid == entryid,
                                                       UserEntry.userfeedid == UserFeeds.id).first()

    if current_state is None:
        logger.info("no userEntry found, adding a new one...")

        entry = db_session.query(Entry).filter(Entry.id == entryid).first()
        uf_id = db_session.query(UserFeeds).filter(UserFeeds.userid == user.id,
                                                   UserFeeds.feedid == entry.feed_id).first().id

        new_user_entry = UserEntry(entryid, user.id, userfeedid=uf_id, starred=True, unread=True)
        db_session.add(new_user_entry)
        db_session.commit()
        return True

    qry = db_session.query(UserEntry).filter(UserEntry.id == current_state.id)

    # okay... if this line doesn't exist, we need to create a new one.

    # this should actually check if it exists, and add record if not.
    # which is a higher function that should be shared with change/add user tags

    # my entire model here for stars is bogus.  Tags and stars probably need to be separate tables
    # sigh.. one entry can have many tags per client, but each entry can only have a single star state (per client)
    if current_state:
        if current_state.starred:

            logger.debug('current state was: {0}'.format(current_state.starred))

            qry.update({"starred": False})
            db_session.commit()

        else:
            logger.debug(current_state.starred)
            qry.update({"starred": True})
            db_session.commit()

        return True

    else:
        return False


def change_user_tags(user, entries):

    return {'taglist': 1}


def changeview(user):

    """ Alternate between compressed and full view of entries"""

    print 'changeview activated!'
    logger.info("attempting to change view state for user: {0}, id: {1}".format(user.nickname, user.id))

    current_state = db_session.query(UserPrefs).filter_by(userid=user.id).first()

    if current_state.compressed_view:
        db_session.query(UserPrefs).filter_by(userid=user.id).update({"compressed_view": False})

    else:
        db_session.query(UserPrefs).filter_by(userid=user.id).update({"compressed_view": True})

    db_session.commit()

    return

