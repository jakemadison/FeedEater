from flask import *
from flask import redirect, url_for, request, g, jsonify  # , render_template, flash, session
from flask.ext.login import current_user  # , login_user, logout_user, login_required
from feedeater.config import configs as c
from feedeater.controller import user_manage_feeds
from feedeater.controller import user_manage_entries

basedir = c.get('basedir')
app = Blueprint('entries', __name__, static_folder=basedir+'/display/static',
                template_folder=basedir+'/display/templates')


@app.before_request
def before_request():
    print "\n\n\nNEW ENTRIES REQUEST: "
    g.user = current_user


#####
# Functions for all entries:
#####

@app.route('/recalculate_entries', methods=['POST', 'GET'])
def recalculate_entries():

    print "recalculating entries...."
    user = g.user
    page = int(request.args.get('page_id', None))

    if page is None:
        page = 1

    print 'page: ', page
    g.page = page

    entries, pager, total_records = user_manage_feeds.recalculate_entries(user, page)
    prefs = user_manage_feeds.get_user_prefs(user)

    return jsonify(success=True, e=entries, compressed_view=prefs, pager=pager, total_records=total_records)


@app.route('/get_unread_count', methods=['GET'])
def unread_count():

    user = g.user

    # Ok, so currently this is just using "feed_id", I probably actually want to send "uf_id"

    feed_id = request.args.get('feed', '', type=int)
    print feed_id

    result = user_manage_feeds.get_unread_count(feed_id, user)
    print result

    return jsonify(success=True, count=result)


#####
# Functions for single entries:
#####

@app.route('/tags', methods=['POST'])
def change_tags():

    user = g.user
    tag_text = request.form['tagtext']
    tag_id = request.form['tagid']

    print tag_text, tag_id

    if g.user.is_authenticated():
        tags = user_manage_feeds.change_user_tags(user)
    else:
        return redirect(request.args.get('next') or url_for('index'))

    return jsonify(title='Home', tags=tags)


@app.route('/star', methods=['POST'])
def toggle_star():

    user = g.user
    entryid = request.form['starid']
    entryid = entryid[5:]
    print entryid

    # right.. so before i made the decision to only add an entry when needed..

    result = user_manage_feeds.change_star_state(user, entryid)

    print result

    return jsonify({"result": result})


@app.route('/mark_as_read', methods=['POST'])
def markAsRead():
    user = g.user
    entry_id = request.form['entry_id']
    print 'marking entry: {e} as read for user: {u}'.format(e=entry_id, u=user.nickname)

    user_manage_entries.mark_entry_read(entry_id, user.id)

    return jsonify(success=True)







