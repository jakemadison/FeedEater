from getfeeds import feed_request
from feedeater.database.models import Feed
from storefeeds import add_entry
import concurrent.futures
import Queue

import logging
from feedeater import setup_logger
logger = logging.getLogger(__name__)
setup_logger(logger)
logger.setLevel(logging.DEBUG)



fin_q = []
len_feeds = 0


def main(feed_list=None):

    """this function should ONLY deal with queue management between get and store functions"""

    fin_q[:] = []

    logger.debug("fin_q: {0}".format(fin_q))

    res_q = Queue.Queue()
    # kill = False

    if not feed_list:
        return False

    def c_store():

        kill = False

        while True:

            if all(each.done() for each in p_futures):
                print "future is DONE"
                kill = True

            if kill and res_q.empty():  # you can only quit when all your work is done
                break
            try:
                item = res_q.get(block=False)
            except Queue.Empty:
                pass

            else:
                logger.debug("grabbing item "+"size: {0}".format(res_q.qsize()))
                add_entry(item)

                logger.debug('...done storing')

                # When done storing, add feed_id to "finished queue"
                fin_q.append(item['posts'][0]['feed_id'])

                #A different polling view can then grab everything off of the 'finished' queue

    def p_call(f):
        logger.debug('Putting Item')
        res_q.put(feed_request(f, get_meta=False))
        logger.info(" net request done", "size: {0}".format(res_q.qsize()))


    #TODO: move this to configs file:
    # optimize network-bound producer pool here:
    p_pool = 10  # 5
    p_exec = concurrent.futures.ThreadPoolExecutor(max_workers=p_pool)
    p_futures = [p_exec.submit(p_call, feed) for feed in feed_list]

    # p_futures = [p_exec.submit(lambda f: res_q.put(feed_request(f, get_meta=False)), feed) for feed in feed_list]

    # optimize DB/IO-bound consumer pool here:
    c_pool = 10  # even SQLite can do concurrency!

    c_exec = concurrent.futures.ThreadPoolExecutor(max_workers=c_pool)
    c_futures = [c_exec.submit(c_store) for e in range(c_pool)]  # start a consumer instance for every worker

    logger.debug("just return to caller now...")

    # wait for all producer futures to finish:
    # concurrent.futures.wait(p_futures)  # it's probably this one that's stopping stuff.

    # send kill to consumers:
    # kill = True

    # wait for consumers to wrap up pending jobs: (if we want to block, that is)
    #concurrent.futures.wait(c_futures)
    logger.debug("done!!!!")
    logger.info("fin_q: {0}".format(fin_q))


def get_all_feeds():
    """retrieve all feeds subscribed to by all users"""

    get_feeds = Feed.query.all()
    feeds = []

    for each in get_feeds:
        logger.info('retrieving subscribed feed from DB: {0}'.format(each.feed_url))
        feeds.append(each.feed_url)

    return feeds


def update_all_feeds():
    try:
        feed_list = get_all_feeds()
        logger.debug('feedlist: {0}'.format(feed_list))
        main(feed_list)
    except Exception, e:
        logger.exception('exception!!!', str(e))

        return 1
    else:
        return 0


if __name__ == "__main__":

    import sys
    # put all cron-based stuff here, ie. all feeds for all subscribed users
    # this is entry point for running backend cron updates daily
    ret_code = update_all_feeds()
    sys.exit(ret_code)

