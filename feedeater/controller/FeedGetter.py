from getfeeds import feed_request
from feedeater.database.models import Feed
from storefeeds import add_entry, store_feed_data
import concurrent.futures
import Queue

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

    res_q = Queue.Queue()
    kill = False

    if not feed_list:
        feed_list = get_all_feeds()

    def c_store():
        while True:
            if kill and res_q.empty():  # you can only quit when all your work is done
                break
            try:
                item = res_q.get(block=False)
            except Queue.Empty:
                pass

            else:
                if item['meta']:
                    store_feed_data(item['meta'])

                for post in item['posts']:
                    print 'storing post....', post.get("title"), post.get("published")
                    add_entry(post)

    def p_call(url):
        print 'getting feed, ', url
        res = feed_request(url, get_meta=True)
        if res:
            res_q.put(res)

    #TODO: move this to configs file:

    # optimize network-bound producer pool here
    p_pool = 5  # 5
    p_exec = concurrent.futures.ThreadPoolExecutor(max_workers=p_pool)
    p_futures = [p_exec.submit(p_call, feed) for feed in feed_list]

     # optimize DB/IO-bound consumer pool here
    c_pool = 1
    c_exec = concurrent.futures.ThreadPoolExecutor(max_workers=c_pool)
    c_futures = [c_exec.submit(c_store) for e in range(c_pool)]  # start a consumer instance for every worker

    # wait for all producer futures to finish:
    concurrent.futures.wait(p_futures)

    # send kill to consumers:
    kill = True

    # wait for consumers to wrap up pending jobs: (if we want to block, that is)
    #concurrent.futures.wait(c_futures)


if __name__ == "__main__":

    # put all cron-based stuff here, ie. all feeds for all subscribed users
    # this is entry point for running backend cron updates daily

    main()

