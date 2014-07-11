import feedfinder
__author__ = 'jakemadison'


# on success, this now returns a feed object, instead of just the URL
def parsefeed(url):

    """instead of rolling own, this just uses feedfinder now.  Let's keep this function as a hook though
    to add more functionality down the line: eg, multiple results per feed_find"""

    try:
        print 'using feed finder'
        res = feedfinder.feeds(url)
        feed_len = len(res)

        if res:
            print '#', feed_len, 'feeds found: ',
            for each in res:
                print each,
            print

            return res, feed_len

        else:
            print "no results found..."
            return False, 0

    except Exception, e:
        print "error!", str(e)
        return False


u = 'http://seriously.dontusethiscode.com/feed.rss'
u = 'seriously.dontusethiscode.com'
u = 'http://blog.yimmyayo.com/'
if __name__ == '__main__':
    x = parsefeed(u)
    print 'final:', x