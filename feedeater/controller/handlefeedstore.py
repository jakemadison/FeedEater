# from feedeater.database.models import Feed
#
#
# def get_stored_feeds():
#
#     get_feeds = Feed.query.all()
#
#     feeds = []
#     for each in get_feeds:  # this could probably be a list comp..
#         print 'retrieving subscribed feed from DB: ', each.feed_url
#         feeds.append(each.feed_url)
#
#     return feeds
#
#
# # okay, so I don't need to get feed title every time, just on feed add.
# # even still, this covers a lot of similar ground to "get feeds"
# def add_new_feed(user, url):
#     # check if feed exists in feed table, if not exists, add then pull entries and feed desc. store properly in
#     # entries, associate with user.
#     # i wonder if I can use this search function somehow find feed links...
#     # http://www.rsssearchhub.com/
#
#     pass
#
#
# def remove_feed(user, url):
#     pass
#
#
#
#
# # feeds = (['http://tanacetum-vulgare.tumblr.com/rss','http://www.reddit.com/r/python/.rss',
# # 'http://xkcd.com/rss.xml', 'i am a malformed feed url', 'http://feeds.feedburner.com/dearcoquette#_=_'])
# # feeds = ['http://ancientpeoples.tumblr.com/rss', 'http://www.reddit.com/r/pystats/.rss',
# #          'http://www.reddit.com/r/pygame/.rss', 'http://www.reddit.com/r/flask/.rss',
# #          'http://xkcd.com/rss.xml', 'http://www.reddit.com/r/python/.rss']