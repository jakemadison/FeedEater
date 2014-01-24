#attempt to open DB connection, and
#store entries..
#from models import Entry, Feed
#from controller import db_session
from feedeater.database import models
# from display import db  # TODO this is pretty confusing db the module vs display.db attribute
from feedeater import db
db_session = db.session

# TODO: incorporate some damn exception catching already


def add_entry(entry, feed_id=0):

    try:
        print '..................storing.........................'
        stored_ent = db_session.query(models.Entry).filter_by(link=entry.get("link")).first()
        print '\n\n>>>>>> @@@@@@@@@', stored_ent, '\n'

        # Even if it is in db it might be updated since last time.
        if stored_ent is not None and stored_ent.updated is entry.get("updated"):
            return

        # It is not really updated if updated is set to 1.
        if entry.get("updated") is 1:
            return

        if stored_ent:
            db_session.query(models.Entry).filter_by(id=stored_ent.id).update(
                {
                    "published": entry.get("published"),
                    "updated": entry.get("updated"),
                    "title": entry.get("title"),
                    "content": entry.get("content"),
                    "description": entry.get("description"),
                    "link": entry.get("link"),
                    "remote_id": entry.get("id"),
                    "feed_id": feed_id,
                })

            # logger.debug("Updating entry with id: {0}".format(entry.get("id")))

            db_session.commit()

        else:
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


def store_meta(meta):

    title = meta["feed_title"]
    link = meta["feed_link"]
    print '===================> storing meta_data in feed table', title, link

    # check for existing in feed table:
    existing = db_session.query(models.Feed).filter(models.Feed.feed_url == link).all()
    print '\n>>>>>>>>>>>>>>>>>>>>>>>', existing

    if not existing:
        print "------------>>>no record found for ", link

        new_feed = models.Feed(feed_url=link,
                               title=title,
                               subscribers=1)

        db_session.add(new_feed)
        db_session.commit()

    else:
        print "------------>>>record found for ", existing

            # could add extra code here to update name if changed.

    # if not exists, add to feed table



            # logger.debug(u"Adding new entry with id: {0}".format(entry.get("id")))



    # either way, add association to userfeed table if doesn't exist on userfeed table already, that is..





# res = feed_request('http://www.reddit.com/r/python/.rss')
#
#
# for each in res['posts']:
#     print 'storing post....', each.get("title"), each.get("published")
#     add_entry(each)
#
# print 'done!'