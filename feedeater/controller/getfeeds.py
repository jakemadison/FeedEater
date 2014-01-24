import time
import feedparser
from feedeater.config import configs


def feed_request(url, get_meta=True):

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
        print str(e)

    if res:
        posts = []
        print 'length of entries: {0}'.format(len(res['entries']))

        for entry in res['entries']:

            post = None

            try:
                # print 'receiving post: {0}'.format(entry.get("title"))
                print 'getting post....{0}'.format(entry.get("title", "No title").encode('utf-8')).strip("\n")[:70]
                post = {
                    "title": entry.get("title", "No title").encode('utf-8'),
                    "link": entry.get("link", "#"),
                    "id": entry.get("id", "No Id"),
                    "published": time_parser(entry.get("published_parsed")),
                    "updated": time_parser(entry.get("updated_parsed"), update_time=True),
                    "description": entry.get("description", "").encode('utf-8'),
                    "content": entry.get("content", [{}])[0].get("value", entry.get("description", "").encode('utf-8')),
                }
            except Exception, e:
                print str(e)
                print '!!!!!!'
                continue

            posts.append(post)

        meta = None
        if get_meta:
            try:
                meta = {
                    "feed_title": res['channel'].get('title', "no feed title"),
                    "feed_url": url,
                    "feed_original_site": res['channel']['link'],
                    "feed_description": res['channel'].get('description', "no description available")
                }
            except Exception, e:
                print str(e)
                print '!!!!!!!!!!'

        feed_data = {"parse_obj": res, "posts": posts, "meta": meta}
        return feed_data


test_url = 'http://dir.yahoo.com/rss/dir/getrss.php?rec_games_video'
test2 = 'http://www.reddit.com/r/python/.rss'
test3 = 'http://xkcd.com/rss.xml'

if __name__ == "__main__":
    import storefeeds
    feed_result = feed_request(test3, get_meta=True)
    storefeeds.store_meta(feed_result["meta"])