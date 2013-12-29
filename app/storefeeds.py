#attempt to open DB connection, and
#store entries..
from models import Entry, Feed
from app import db_session
from getfeeds import feed_request


def add_entry(entry, feed_id=0):

    stored_ent = db_session.query(Entry).filter_by(link=entry.get("link")).first()

    # Even if it is in db it might be updated since last time.
    if stored_ent is not None and stored_ent.updated is entry.get("updated"):
        return

    # It is not really updated if updated is set to 1.
    if entry.get("updated") is 1:
        return

    if stored_ent:
        db_session.query(Entry).filter_by(id=stored_ent.id).update(
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
        new_entry = Entry(
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


res = feed_request('http://www.reddit.com/r/python/.rss')


for each in res['posts']:
    print 'storing post....', each.get("title"), each.get("published")
    add_entry(each)

print 'done!'