from getfeeds import feed_request
from storefeeds import add_entry
import concurrent.futures
import Queue


# I need a function to pull existing feeds here.. but for now:
# also need a function (DB proc?) to remove feeds when there are zero subs
# that will all be handled by display object though
def get_subscribed_feeds():
    feeds = ['http://www.reddit.com/r/python/.rss', 'http://xkcd.com/rss.xml', 'i am a malformed feed url', 'http://feeds.feedburner.com/dearcoquette#_=_']
    return feeds


def main():

    res_q = Queue.Queue()
    kill = False

    def c_store():
        while True:
            if kill and res_q.empty():  # you can only quit when all your work is done
                break
            try:
                item = res_q.get(block=False)
            except Queue.Empty:
                pass
            else:
                for post in item['posts']:
                    print 'storing post....', post.get("title"), post.get("published")
                    add_entry(post)

    def p_call(url):
        print 'getting feed, ', url
        res = feed_request(url)
        if res:
            res_q.put(res)

    # optimize network-bound producer pool here
    p_exec = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    p_futures = [p_exec.submit(p_call, feed) for feed in get_subscribed_feeds()]

     # optimize DB/IO-bound consumer pool here
    c_exec = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    c_futures = [c_exec.submit(c_store) for e in range(1)]  # start a consumer instance for every worker

    # wait for all producer futures to finish:
    concurrent.futures.wait(p_futures)

    # send kill to consumers:
    kill = True

    # wait for consumers to wrap up pending jobs: (if we want to block, that is)
    concurrent.futures.wait(c_futures)


if __name__ == "__main__":
    main()

















