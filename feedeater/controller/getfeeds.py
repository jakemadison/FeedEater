import time
import feedparser
from feedeater.config import configs


import logging
from feedeater import setup_logger
logger = logging.getLogger(__name__)
setup_logger(logger)
logger.setLevel(logging.DEBUG)


def get_feed_meta(url):

    """I'm not entirely sure this function ever actually runs."""

    logger.info('running get_feed_meta function')

    try:
        res = feedparser.parse(url, configs.get('User-Agent'))

    except Exception, e:
        logger.exception('error!')
        return False

    if res:
        logger.debug('{0}, {1}, {2}'.format(res.feed, res.status, res.version))

    try:
        meta = {
            "feed_title": res['channel'].get('title', "no feed title"),
            "feed_url": url,
            "feed_original_site": res['channel']['link'],
            "feed_description": res['channel'].get('description', "no description available")
        }
    except Exception, e:
        logger.exception(str(e))
        logger.exception('!!!!!!!!!!')

    else:
        return meta


def feed_request(f, get_meta=False):

    url = f['url']
    feed_id = f['feed_id']

    def time_parser(time_str, update_time=False):
        """
        This function parses the time str from feedparser. Feeds may not
        always include the time for update, and published. So if it is
        in the feed the current time will be set for those values.

        If the update time is missing for the feed the function will set it
        to 1. If the current time is used it will end up wrong in the DB if
        the entry already exist in the DB.

        :param time_str The time str to be parsed.

        :param update_time Set to true if it is the update time that is parsed.

        :return UNIX timestamp
        """

        if time_str is None:
            if update_time:
                return 1
            else:
                return time.time()

        else:
            return time.mktime(time_str)

    res = None

    try:
        res = feedparser.parse(url, configs.get('User-Agent'))
    except Exception, e:
        logger.exception('error!')

    if res:

        posts = []
        # print 'length of entries: {0}'.format(len(res['entries']))
        # there needs to be a "if length entries > 0 here

        for entry in res['entries']:

            post = None

            try:
                post = {
                    "feed_id": feed_id,
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", "#"),
                    "id": entry.get("id", "No Id"),
                    "published": time_parser(entry.get("published_parsed")),
                    "updated": time_parser(entry.get("updated_parsed"), update_time=True),
                    "description": entry.get("description", ""),
                    "content": entry.get("content", [{}])[0].get("value", entry.get("description", "")),
                }
            except Exception, e:
                logger.exception('error!')
                continue

            posts.append(post)

        meta = None
        if get_meta:
            try:
                meta = {
                    "feed_title": res['channel'].get('title', "no feed title"),
                    "feed_url": url,
                    "feed_original_site": res['channel']['link'],
                    "feed_description": res['channel'].get('description', "no description available"),
                    "feed_id": feed_id
                }
            except Exception, e:
                logger.exception('error!!')

        feed_data = {"parse_obj": res, "posts": posts, "meta": meta}
        return feed_data


test_url = 'http://dir.yahoo.com/rss/dir/getrss.php?rec_games_video'
test2 = 'http://www.reddit.com/r/python/.rss'
test3 = 'http://xkcd.com/rss.xml'
test4 = {'url': 'http://www.shiningrocksoftware.com/?feed=rss2', 'feed_id': None}

if __name__ == "__main__":
    import storefeeds
    feed_result = feed_request(test4, get_meta=False)
    #storefeeds.store_feed_data(feed_result["meta"])