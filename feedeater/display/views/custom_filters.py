
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