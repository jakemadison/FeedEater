from flask import *
from flask import flash, redirect, url_for, request, g, jsonify
from flask.ext.login import current_user
from feedeater.config import configs as c
from feedeater.controller import user_manage_feeds
from feedeater.controller import user_manage_entries

basedir = c.get('basedir')
app = Blueprint('subscriptions', __name__, static_folder=basedir+'/display/static',
                template_folder=basedir+'/display/templates')


@app.before_request
def before_blueprint_request():
    print "NEW SUBSCRIPTIONS.PY REQUEST"
    g.user = current_user


#####
# Functions for all subscriptions:
#####

@app.route('/refreshfeeds', methods=['POST', 'GET'])
def ref_feeds():
    print 'ref_feeds view function active'
    user = g.user
    user_manage_feeds.main(user)

    return jsonify(success=True)


@app.route('/get_progress', methods=['GET'])
def get_progress():

    user = g.user
    print "made it to get_progress"

    fin_list = user_manage_feeds.get_progress()
    feed_len = user_manage_feeds.get_user_feeds(user)

    print len(feed_len['feed_data'])

    if len(fin_list) >= len(feed_len['feed_data']):
        done = True
    else:
        done = False

    return jsonify(fin=fin_list, done=done)


@app.route('/get_user_subs', methods=['GET'])
def get_user_subs():
    print 'getting user subs and cats'
    user = g.user
    sub_list = user_manage_feeds.get_user_feeds(user)
    cats = sub_list['cat_list']
    feed_data = sub_list['feed_data']
    cats = [str(x) for x in (sorted(cats))]

    print "categories loaded and sorted from get request.."

    return jsonify(subs=feed_data, cats=cats, success=True)


#####
# Functions for editing single subscriptions:
#####

@app.route('/add_feed', methods=['POST'])
def add_feed():

    # this could be a lot smarter.  What if user is already subscribed to one of the feeds returned
    # in a multiple feed response scenario?

    print "........]]]]] add_feed has been activated"

    user = g.user

    try:
        data = request.form["url"]
        print '...............', data

    except Exception, e:
        print e
        return jsonify(msg="add_feed failure")

    # this doesn't check for bad input..
    # need to validate if URL / if empty here (or on client side?)

    # result should always return a "message", "data" dict
    result = user_manage_feeds.add_user_feed(user, data)

    print result

    # here, if multiple results, return as such, with list of possible feeds
    # down the line, might be nice to show a preview or at least get the title/desc
    # of the feeds.  Anyways, client side does a popup, and then we just post back here with
    # the feed URL. er, well, iteratively... (client side? server side?)

    if result['message'] == "already_associated":
        msg = "Already Subscribed  :)"
        category = "info"

    elif result['message'] == "success":
        msg = "Successfully added new feed  :D"
        category = "success"

    elif result['message'] == "error_adding_feed":
        msg = "Unknown error adding feed  :o"
        category = "error"

    elif result['message'] == "no_feed_found":
        msg = "No rss feed found at that url  :("
        category = "error"

    elif result['message'] == "multiple_feeds_found":
        msg = "Many feeds were found!"
        category = "multi"

    else:
        msg = "Unknown error ????"
        category = "error"

    return jsonify(msg=msg, category=category, f=result['data'])


@app.route('/changecat', methods=['POST'])
def change_cats():

    print "++++++++++++++++++++++++"
    cat_old = request.form['current_cat_name']
    cat_new = request.form['cat_new']
    uf_id = request.form['uf_id']
    print cat_old
    print cat_new
    print uf_id
    result = user_manage_feeds.apply_feed_category(cat_new, uf_id, remove=False)
    print result
    flash(result, "info")
    return redirect(url_for('/'))


@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    print "removing feed from user_feeds"

    user = g.user
    feedid = request.form['ufid']
    result = user_manage_feeds.remove_user_feed(user, feedid)

    if result == "successfully deleted":
        msg = "Successfully removed  :D"
        category = "success"
    elif result == "error_deleting_feed":
        msg = "Unknown error removing feed  :("
        category = "error"

    elif result == "feed_id not found":
        msg = "Feed Id Not found  :("
        category = "error"
    else:
        msg = "I'm not sure what happened there.."
        category = "error"

    print "finished removing feed"

    return jsonify(msg=msg, category=category, f=None)


#####
# Functions for changing subscription display:
#####

@app.route('/togglecategory', methods=['POST', 'GET'])
def toggle_category():

    print 'entering toggle_category function'
    user = g.user
    print user

    cat = request.args.get('catname', None)

    print 'this is category: ', cat

    if not cat:
        print 'I do not have a category for some reason'
        return jsonify(success=False)

    all_on = user_manage_feeds.toggle_category(user, cat)

    print 'done toggling category'
    return jsonify(success=True, all=all_on)


@app.route('/onefeedonly', methods=['GET'])
def one_feed_only():
    print 'changing to one feed only'

    uf_id = request.args.get('uf_id', None)

    if not uf_id:
        print 'i failed to get an Id!'
        return jsonify(success=False)

    user = g.user
    user_manage_feeds.single_active(user, uf_id)

    return jsonify(success=True)


@app.route('/allfeeds', methods=['GET'])
def show_all_feeds():

    print "entered all feeds function"
    user = g.user
    user_manage_feeds.all_active(user)

    return jsonify(success=True)


@app.route('/change_active', methods=['GET', 'POST'])
def change_active():

    print "----- entering change active"
    uf_id = request.args.get('uf_id')
    print uf_id
    user_manage_feeds.update_is_active(uf_id)

    print 'finished change_active.'

    return jsonify(success=True)


@app.route('/change_view', methods=['POST'])
def change_view():

    user = g.user
    print 'user: ', user.nickname, user.id
    user_manage_entries.changeview(user)

    print "done! changeview!"

    return jsonify(success=True)


@app.route('/starred_only', methods=['POST'])
def only_starred():

    user = g.user

    # this should run recalc entries.. but with all feeds considered active (?)
    # or should you only see starred entries from active ones?
    # anyways, either way, just send starred_only=True (default to false on sig
    # of function) and then just add an extra where clause for UserEntry.starred = True.

    # result = user_manage_feeds.recalculate_entries()

    return False


