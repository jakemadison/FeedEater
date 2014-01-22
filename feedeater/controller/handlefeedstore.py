from feedeater.database.models import Feed


def get_stored_feeds():

    #TODO: expand logic here to query based on logged in user and/or update time or whatever.
    get_feeds = Feed.query.all()

    feeds = []
    for each in get_feeds:

        print 'retrieving feed: ', each.feed_url
        feeds.append(each.feed_url)

    return feeds





# feeds = (['http://tanacetum-vulgare.tumblr.com/rss','http://www.reddit.com/r/python/.rss',
# 'http://xkcd.com/rss.xml', 'i am a malformed feed url', 'http://feeds.feedburner.com/dearcoquette#_=_'])
# feeds = ['http://ancientpeoples.tumblr.com/rss', 'http://www.reddit.com/r/pystats/.rss',
#          'http://www.reddit.com/r/pygame/.rss', 'http://www.reddit.com/r/flask/.rss',
#          'http://xkcd.com/rss.xml', 'http://www.reddit.com/r/python/.rss']