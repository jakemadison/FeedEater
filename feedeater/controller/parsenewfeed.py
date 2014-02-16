import feedparser
from feedeater.config import configs
import feedfinder
__author__ = 'jakemadison'


# on success, this now returns a feed object, instead of just the URL
def parsefeed(url):

    """take in a URL and attempt to return a valid rss url from that page.
    This should take in a URL and should attempt all kinds of magic to send back a valid RSS.
    Possibilities include web crawling, checking known domains (eg, tumblr, add known rss path)"""

    def test_url(u):

        f = feedparser.parse(url, configs.get('User-Agent'))

        if not f:
            return False

        if f.bozo:
            # are we supposed to fail on bozo exception no matter what?
            print f.bozo_exception
            # return False

        if f.feed == {}:
            print 'no content'
            return False

        if f.status == '404':
            return False

        return f

    if False:
        return url

    else:
        try:
            print 'using feed finder'
            res = feedfinder.feed(url)
            if res:
                # feed = test_url(res)
                return res
            else:
                print "no results found..."

        except Exception, e:
            print "error!", str(e)
            return False

    # what do we do if there are multiple results? have user choose?



u = 'http://seriously.dontusethiscode.com/feed.rss'
u = 'seriously.dontusethiscode.com'
u = 'http://blog.yimmyayo.com/'
if __name__ == '__main__':
    x = parsefeed(u)
    print 'final:', x