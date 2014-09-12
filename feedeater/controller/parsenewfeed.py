import feedfinder
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
        res = feedfinder.feeds(url)
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


u = 'http://seriously.dontusethiscode.com/feed.rss'
u = 'seriously.dontusethiscode.com'
u = 'http://blog.yimmyayo.com/'
if __name__ == '__main__':
    x = parsefeed(u)
    logger.debug('final: {0}'.format(x))