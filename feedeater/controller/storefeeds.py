from feedeater.database import models
# from display import db  # TODO this is pretty confusing db the module vs display.db attribute
from feedeater import db
db_session = db.session

# TODO: incorporate some damn exception catching already

# Okay, the structure of this has been confused because of dev scaffolding
# basically, the logic should go: user -> feedlist -> feed -> entries
# every entry has a feed, every feed has a user, (via feedlist assoc. table)
# update times are feed specific, tags are feedlist specific


def get_feed_id(feed_url):
    pass


def store_feed_data(meta):

    title = meta["feed_title"]
    feed_url = meta["feed_url"]
    site = meta["feed_original_site"]
    description = meta["feed_description"]
    print '===================> storing meta_data in feed table', title, site

    # check for existing in feed table:
    existing = db_session.query(models.Feed).filter(models.Feed.feed_url == feed_url).first()  # all() returns list.
    # can I return id here?

    if existing:
        # check for changes to existing meta_data (feed title, description, etc)
        # this might be a candidate to remove to only cron jobs to speed everything up
        try:
            if existing.feed_site != site or existing.description != description or existing.title != title:
                print "\n>>>>>>>>>>>>>>>>>>>>>>>update information.. updating DB"
                db_session.query(models.Feed).filter_by(id=existing.id).update(
                                {
                                    "title": title,
                                    "feed_site": site,
                                    "description": description
                                })
                db_session.commit()

            else:
                print "\n>>>>>>>>>>>>>>>>>>>>>>>no changes in feed detected.. don't even worry about it."

        except Exception, e:  # this should be a less general exception..
            print '>>>>>>error!!!!!'
            print str(e)
            db_session.rollback()

    else:
        print "------------>>>no record found for ", feed_url, site
        new_feed = models.Feed(feed_url=feed_url,
                               title=title,
                               feed_site=site,
                               subscribers=1,
                               description=description)

        db_session.add(new_feed)  # does this return the ID of the feed??

        #TODO: this isn't going to work, except on adding of new feeds.
        # this needs to be moved somewhere else, check for feed id, and use that
        # to throw at entry to get correct feed_id.

        db_session.commit()


    # either way, add association to userfeed table if doesn't exist on userfeed table already, that is..
    #
    # which means that this function needs userinfo...
    # which actually, should be handled a level above...?


def store_user_feeds(feed, user=None):
    print "storing user-feed assoc. for ", feed


def add_entry(entry, feed_id=0):

    try:
        stored_ent = db_session.query(models.Entry).filter_by(link=entry.get("link")).first()

        # Even if it is in db it might be updated since last time.
        if stored_ent is not None and stored_ent.updated is entry.get("updated"):
            return

        # It is not really updated if updated is set to 1.
        if entry.get("updated") is 1:
            return

        if stored_ent:
            print 'old entry detected....', stored_ent.title, stored_ent.id

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
                        "feed_id": feed_id
                    })

                # logger.debug("Updating entry with id: {0}".format(entry.get("id")))

                db_session.commit()
            except Exception, e:
                print 'errrror with existing'
                print str(e)
                db_session.rollback()

        else:  # why are content and description storing the same information in all feeds?

            print 'new entry detected...'
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
                feed_id=feed_id
            )

            # logger.debug(u"Adding new entry with id: {0}".format(entry.get("id")))
            db_session.add(new_entry)
            db_session.commit()

    except Exception, e:
        db_session.rollback()
        print 'ERROR!!'
        print str(e)


