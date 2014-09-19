from feedeater.database.models import UserFeeds, Entry, UserEntry, UserPrefs
from feedeater import db
from sqlalchemy import exc

db_session = db.session

import logging
from feedeater import setup_logger
logger = logging.getLogger(__name__)
setup_logger(logger)
logger.setLevel(logging.DEBUG)


def mark_entry_read(entryid, userid):

    """ check for existence of user_feed_entry for user/entryid combo
     if exists, make unread = False
     if doesn't exist, make new record with unread=False"""

    logger.info('marking as read, entryid: {0}, userid: {1}'.format(entryid, userid))

    # check current state
    current_state = db_session.query(UserEntry).filter(UserFeeds.userid == userid,
                                                   UserEntry.entryid == entryid,
                                                   UserEntry.userfeedid == UserFeeds.id).first()

    # add new with unread = False
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

    # TODO: Again, can't we just use "current_state"?
    qry = db_session.query(UserEntry).filter(UserEntry.id == current_state.id)

    qry.update({"unread": False})
    db_session.commit()

    return


def change_star_state(user, entryid):

    # this function is a boolean.. so it shouldn't care what the state originally was
    # it can be state agnostic.  same with the front end.  it only needs to know if
    # toggle at the back was successful or not

    # attempt to get current star state of user/entry:
    current_state = db_session.query(UserEntry).filter(UserFeeds.userid == user.id,
                                                       UserEntry.entryid == entryid,
                                                       UserEntry.userfeedid == UserFeeds.id).first()

    # stars are created on demand, so create one if it doesn't exist
    if current_state is None:
        logger.info("no userEntry found, adding a new one...")

        entry = db_session.query(Entry).filter(Entry.id == entryid).first()
        uf_id = db_session.query(UserFeeds).filter(UserFeeds.userid == user.id,
                                                   UserFeeds.feedid == entry.feed_id).first().id

        # because star state is False by default, if we're creating a new one, it must be true
        new_user_entry = UserEntry(entryid, user.id, userfeedid=uf_id, starred=True, unread=True)
        db_session.add(new_user_entry)
        db_session.commit()
        return True

    #TODO: is this still required? Can we not just use "current_state" above?
    qry = db_session.query(UserEntry).filter(UserEntry.id == current_state.id)

    # okay... if this line doesn't exist, we need to create a new one.

    # this should actually check if it exists, and add record if not.
    # which is a higher function that should be shared with change/add user tags

    # my entire model here for stars is bogus.  Tags and stars probably need to be separate tables
    # sigh.. one entry can have many tags per client, but each entry can only have a single star state (per client)

    # this seems redundant... I'm nixing it for now.
    # if current_state:
    if current_state.starred:

        logger.debug('current state was: {0}'.format(current_state.starred))

        qry.update({"starred": False})
        db_session.commit()

    else:
        logger.debug(current_state.starred)
        qry.update({"starred": True})
        db_session.commit()

    return True

    # else:
    #     return False


def change_user_tags(user, entries):

    # this is essentially a stub for now.
    return {'taglist': 1}


def changeview(user):

    """ Alternate between compressed and full view of entries and save
        that to UserPrefs table"""

    logger.info("attempting to change view state for user: {0}, id: {1}".format(user.nickname, user.id))

    try:
        # find the current state of view
        current_state = db_session.query(UserPrefs).filter_by(userid=user.id).first()

        # whatever it is, make it the opposite
        if current_state.compressed_view:
            db_session.query(UserPrefs).filter_by(userid=user.id).update({"compressed_view": False})

        else:
            db_session.query(UserPrefs).filter_by(userid=user.id).update({"compressed_view": True})

        # now commit
        db_session.commit()

    # TODO: is this the correct way to catch sql errors?
    except exc.SQLAlchemyError, e:
        logger.error('DB exception.  No need for rollback.')

    # this should return a status based on whether DB operation was successful or not.
    # we only rarely care about getting compressed state...
    return

