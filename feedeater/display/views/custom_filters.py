from datetime import datetime, timedelta
import urlparse


#the template truncate function doesn't quite do what I want it to.
def truncate_title(title):

    if not title:
        title = 'no title'  # not needed.

    if len(title) > 50:
        temp_t = title[0:50]
        k = temp_t.rfind(" ")
        if k:
            short_title = temp_t[:k]+"..."
            return short_title
        else:
            short_title = temp_t[:47]+"..."
            return short_title

    return title


def parse_time(time):
    parse_date = datetime.fromtimestamp(time)
    now = datetime.now()
    starter_word = ''

    if parse_date >= now - timedelta(days=7):  # this week?
        if parse_date >= now - timedelta(days=1):  # yesterday? (this checks for within 24hours.
                                                    # need > midnight
            starter_word = ''
            form = '%I:%M%p'

        else:
            form = '%a %I:%M%p'

    else:
        form = '%I:%M%p %m/%d/%Y'

    return starter_word + parse_date.strftime(form).lstrip('0')


# okay, but here's a problem... what if we want custom feed titles?
# then this does belong elsewhere, either models.py or manage_feeds
# orrrr... add user_feed.title || feed.remote_id|url_base - if user_feed.title is null, go for url_base?
def url_base(url):
    return urlparse.urlparse(url).netloc.lstrip('www.')