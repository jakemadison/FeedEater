from __future__ import print_function
# import feedfinder
import feedfinder_new
__author__ = 'jakemadison'


import logging
from feedeater import setup_logger
logger = logging.getLogger(__name__)
setup_logger(logger)
logger.setLevel(logging.DEBUG)


# on success, this returns a feed object, instead of just the URL
def parsefeed(url):

    """this just attaches to feedfinder.  Let's keep this function as a hook though
    to add more functionality down the line: eg, multiple results per feed_find"""

    try:
        logger.info('using feed finder')
        # res = feedfinder.feeds(url)
        res = feedfinder_new.feeds(url)
        feed_len = len(res)

        if res:
            logger.info('{0} feeds found: {1}'.format(feed_len, res))
            return res, feed_len

        else:
            logger.warn("no results found...")
            return False, 0

    except Exception, e:
        logger.exception("error!")
        return False


if __name__ == '__main__':

    import time
    start_time = time.time()

    # test case for feed finder:
    u_list = ['http://ancientpeoples.tumblr.com/rss',
              'http://xkcd.com/rss.xml',
              'http://www.reddit.com/r/python/.rss',
              'http://maruthecat.tumblr.com/rss',
              'http://feeds.nationalgeographic.com/ng/photography/photo-of-the-day/',
              'http://feeds.feedblitz.com/hackersgonnahack',
              'http://www.shiningrocksoftware.com/?feed=rss2',
              'http://seriously.dontusethiscode.com/feed.rss',
              'http://blog.yimmyayo.com/rss',
              'http://dearcoquette.com/rss',
                'http://www.reddit.com/r/flask/.rss',
                'http://www.reddit.com/r/pygame/.rss',
                'http://lukauskas.co.uk/feed.xml',
                'http://feeds.feedburner.com/TheMouseVsThePython',
                'http://www.parisdailyphoto.com/feeds/posts/default',
                'http://cabinporn.com/rss',
                'http://candide.tumblr.com/rss',
                'http://www.rsspect.com/rss/asw.xml',
                'http://www.smbc-comics.com/rss.php',
                'http://www.penny-arcade.com/rss.xml',
                'http://rsspect.com/rss/qwantz.xml',
                'http://feeds.feedburner.com/oatmealfeed',
                'http://howstuffworks.tumblr.com/rss',
                'http://skeletorislove.tumblr.com/rss',
                'http://syruptrap.ca/feed/',
                'http://pythonthusiast.pythonblogs.com/230_pythonthusiast/feeds/rss20',
                'http://acmonette.com/feeds/all.atom.xml',
                'http://westcoastmountainmouse.wordpress.com/feed/',
                'http://www.reddit.com/r/Python/.rss',
                'http://pyvideo.org/video/rss',
                'http://www.reddit.com/r/index.rss',
                'http://xkcd.com/atom.xml',
                'http://vancouver.en.craigslist.ca/search/jjj?query=python&s=0&format=rss',
                'http://www.reddit.com/r/shittyprogramming/.rss',
                'http://www.thestranger.com/seattle/Rss.xml',
                'http://www.thestranger.com/seattle/Rss.xml?category=oid%3A258',
                'http://danielmarin.naukas.com/feed/',
                'http://www.businesscat.happyjar.com/feed/',
                'http://www.businesscat.happyjar.com/comic/coffee/feed/',
                'http://www.businesscat.happyjar.com/feed/atom/',
                'http://digthattreasure.blogspot.com/feeds/posts/default?alt=rss',
                'http://nancyl3ticia.tumblr.com/rss.xml']

    for i, u in enumerate(u_list):
        x = parsefeed(u)
        print('{1}/{2} - final: {0}'.format(x, i+1, len(u_list)))

    print("======>  Total execution time in seconds: {0}".format(time.time() - start_time))
    print('Done.')