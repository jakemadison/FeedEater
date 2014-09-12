from feedeater.database import models
# from display import db  # TODO this is pretty confusing db the module vs display.db attribute
from feedeater import db
db_session = db.session


import logging
from feedeater import setup_logger
logger = logging.getLogger(__name__)
setup_logger(logger, logging.DEBUG)

# TODO: incorporate some damn exception catching already

# basically, the logic should go: user -> feedlist -> feed -> entries
# every entry has a feed, every feed has a user, (via feedlist assoc. table)
# update times are feed specific, tags are feedlist specific

# this whole thing is (making a session?) doing a full transaction on each entry.
# that is HUGELY slowing down overall performance.  look into flush()?
# maybe when concurrency on the DB side is brought into the picture.
# also, context manager, a la: http://docs.sqlalchemy.org/en/latest/orm/session.html, pretty slick.


def store_feed_data(meta):

    title = meta["feed_title"]
    feed_url = meta["feed_url"]
    site = meta["feed_original_site"]
    description = meta["feed_description"]

    logger.info('storing meta_data in feed table')
    logger.debug('{0} - {1}'.format(title, site))

    # check for existing in feed table:
    existing = db_session.query(models.Feed).filter(models.Feed.feed_url == feed_url).first()

    if existing:
        # check for changes to existing meta_data (feed title, description, etc)
        # this might be a candidate to remove to only cron jobs to speed everything up
        try:
            if existing.feed_site != site or existing.description != description or existing.title != title:

                logger.info("\n>>updated information.. updating DB")

                db_session.query(models.Feed).filter_by(id=existing.id).update(
                                {
                                    "title": title,
                                    "feed_site": site,
                                    "description": description
                                })
                db_session.commit()

            else:
                logger.info("\n>>no changes in feed detected.. don't even worry about it.")

        except Exception, e:  # this should be a less general exception..
            logger.exception('>>>>>>error!!!!! rolling back db transaction.')

            db_session.rollback()

    else:
        logger.debug(">>>no record found for {0}, {1}".format(feed_url, site))

        new_feed = models.Feed(feed_url=feed_url,
                               title=title,
                               feed_site=site,
                               subscribers=1,
                               description=description)

        db_session.add(new_feed)

        #TODO: this isn't going to work, except on adding of new feeds.
        # this needs to be moved somewhere else, check for feed id, and use that
        # to throw at entry to get correct feed_id.

        db_session.commit()


def add_entry(entries, update_entries=False):

    for entry in entries['posts']:
        try:
            stored_ent = db_session.query(models.Entry).filter_by(link=entry.get("link")).first()

            # Even if it is in db it might be updated since last time.
            if stored_ent is not None and stored_ent.updated is entry.get("updated"):
                return

            # It is not really updated if updated is set to 1.
            if entry.get("updated") is 1:
                return

            if stored_ent:
                if update_entries:
                    try:
                        db_session.query(models.Entry).filter_by(id=stored_ent.id).update(
                            {
                                "published": entry.get("published"),
                                "updated": entry.get("updated"),
                                "title": entry.get("title"),
                                "content": entry.get("content"),
                                "description": entry.get("description"),
                                "link": entry.get("link"),
                                "remote_id": entry.get("id"),
                                "feed_id": entry.get("feed_id")
                            })

                    except Exception, e:
                        logger.exception('error with existing rolling back db transaction.')
                        db_session.rollback()

            else:
                logger.debug('new entry detected...')
                # okay, so for this one, we need to pass a full feed object to "source" instead
                # of setting feed_id manually...

                new_entry = models.Entry(
                    published=entry.get("published"),
                    updated=entry.get("updated"),
                    title=entry.get("title"),
                    content=entry.get("content"),
                    description=entry.get("description"),
                    link=entry.get("link"),
                    remote_id=entry.get("id"),
                    feed_id=entry.get("feed_id")
                )

                db_session.add(new_entry)

        except Exception, e:
            logger.exception('ERROR!!, rolling back DB')
            db_session.rollback()

    db_session.commit()

