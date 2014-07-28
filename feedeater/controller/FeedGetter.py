from getfeeds import feed_request
from feedeater.database.models import Feed
from storefeeds import add_entry
import concurrent.futures
import Queue


fin_q = []
len_feeds = 0


def get_all_feeds():
    # might refactor out this wrapper.  it's not really doing much right now...

    #TODO: expand logic here to query based on logged in user and/or update time or whatever.
    get_feeds = Feed.query.all()
    feeds = []

    for each in get_feeds:
        print 'retrieving subscribed feed from DB: ', each.feed_url
        feeds.append(each.feed_url)

    return feeds


def main(feed_list=None):

    """this function should ONLY deal with queue management between get and store functions"""

    fin_q[:] = []
    print "fin_q at start", fin_q

    res_q = Queue.Queue()
    # kill = False

    if not feed_list:
        feed_list = get_all_feeds()  # this needs to be changed to fit feed_id in as well.

    def c_store():

        kill = False

        while True:

            # this seems a little hacky..
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
                print "   grabbing item", "size: ", res_q.qsize()
                add_entry(item)
                print '...done storing'

                # When done storing, add item to "finished queue"
                fin_q.append(item['posts'][0]['feed_id'])
                #A different polling view can then grab everything off of the 'finished' queue

    def p_call(f):
        print " Putting Item",
        res_q.put(feed_request(f, get_meta=False))
        print " net request done", "size: ",
        print res_q.qsize()

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

    print "just return to caller now..."

    # wait for all producer futures to finish:
    # concurrent.futures.wait(p_futures)  # it's probably this one that's stopping stuff.

    # send kill to consumers:
    # kill = True

    # wait for consumers to wrap up pending jobs: (if we want to block, that is)
    #concurrent.futures.wait(c_futures)
    print "done!!!!"
    print "fin_q: ", fin_q


if __name__ == "__main__":

    # put all cron-based stuff here, ie. all feeds for all subscribed users
    # this is entry point for running backend cron updates daily
    main()

