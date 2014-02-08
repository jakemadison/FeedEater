from getfeeds import feed_request
from feedeater.database.models import Feed
from storefeeds import add_entry, store_feed_data
import concurrent.futures
import Queue
import time

# I need a function to pull existing feeds here.. but for now:
# also need a function (DB proc?) to remove feeds when there are zero subs
# that will all be handled by display object though


def get_all_feeds():
    # might refactor out this wrapper.  it's not really doing much right now...

    #TODO: expand logic here to query based on logged in user and/or update time or whatever.
    get_feeds = Feed.query.all()
    feeds = []

    for each in get_feeds:  # this could probably be a list comp..
        print 'retrieving subscribed feed from DB: ', each.feed_url
        feeds.append(each.feed_url)

    # feeds = ['http://feeds.nationalgeographic.com/ng/photography/photo-of-the-day/']
    return feeds


def main(feed_list=None):

    """this function should ONLY deal with queue management between get and store functions"""

    res_q = Queue.Queue()
    kill = False

    if not feed_list:
        feed_list = get_all_feeds()  # this needs to be changed to fit feed_id in as well.

    def c_store():
        # time.sleep(30)
        while True:
            if kill and res_q.empty():  # you can only quit when all your work is done
                break
            try:
                item = res_q.get(block=False)
            except Queue.Empty:
                pass

            else:
                # print item
                # print dir(item)

                # if item['meta']:
                    # store_feed_data(item['meta']) #this should not be separate. put it in add_entry()
                print "   grabbing item", "size: ", res_q.qsize()
                add_entry(item)  # add feed_id here...?
                print '...done storing'

    def p_call(f):

        print " Putting Item",
        res_q.put(feed_request(f, get_meta=False))
        print " net request done", "size: ",
        print res_q.qsize()
        #print 'getting feed, ', f['url'], 'at: ', f['feed_id']
        # print f
        # res = feed_request(f, get_meta=False)
        # print 'got res'
        # if res:
        #     res_q.put(res)

    #TODO: move this to configs file:
    #NB: right now this doesn't look paralellel because of single storage pool, and speed of storage
    # optimize network-bound producer pool here
    p_pool = 10  # 5
    p_exec = concurrent.futures.ThreadPoolExecutor(max_workers=p_pool)
    p_futures = [p_exec.submit(p_call, feed) for feed in feed_list]

    # p_futures = [p_exec.submit(lambda f: res_q.put(feed_request(f, get_meta=False)), feed) for feed in feed_list]

     # optimize DB/IO-bound consumer pool here
    c_pool = 10  # apparently sqllite is okay with multiple connections?
    c_exec = concurrent.futures.ThreadPoolExecutor(max_workers=c_pool)
    c_futures = [c_exec.submit(c_store) for e in range(c_pool)]  # start a consumer instance for every worker

    # wait for all producer futures to finish:
    concurrent.futures.wait(p_futures)  # is this making it not parallel?

    # send kill to consumers:
    kill = True

    # wait for consumers to wrap up pending jobs: (if we want to block, that is)
    #concurrent.futures.wait(c_futures)
    print "done!!!!"


if __name__ == "__main__":

    # put all cron-based stuff here, ie. all feeds for all subscribed users
    # this is entry point for running backend cron updates daily

    main()

