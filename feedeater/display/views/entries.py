from flask import *
from flask import redirect, url_for, request, g, jsonify  # , render_template, flash, session
from flask.ext.login import current_user  # , login_user, logout_user, login_required
from feedeater.config import configs as c
from feedeater.controller import user_manage_feeds
import time
#from flask import Markup
#from feedeater import flaskapp
#from feedeater import lm, oid
#from feedeater.display.forms import LoginForm, AddFeedForm
#import sys
#from feedeater.controller import FeedGetter
#from feedeater.database.models import User, ROLE_USER, Entry, UserEntry

basedir = c.get('basedir')
app = Blueprint('entries', __name__, static_folder=basedir+'/display/static',
                template_folder=basedir+'/display/templates')


# this module requires a "recalculate entries" function which will need to take into account
# which categories are active, which page we are currently on.. ah crap that'll be fun..
# how do you recalculate a paging function? are we going to have to manually put
# together a paging sql query?


@app.before_request
def before_request():

    print "\n\n\nNEW ENTRIES REQUEST: "
    g.user = current_user
    # print g.user.nickname, g.user.id



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


@app.route('/recalculate_entries', methods=['POST', 'GET'])
def recalculate_entries():

    # time.sleep(5)

    print "recalculating entries...."
    user = g.user

    print request
    print dir(request)

    # active_list = request.form.getlist('active_list[]')
    # page = request.form['current_page']
    #
    # star = request.form.get('star_only', False)

    active_list = request.args.get('active_list', None)
    page = request.args.get('current_page', 1)
    star = request.args.get('star_only', False)

    active_list = [int(a.replace('uf_id', '')) for a in active_list]
    print 'active list......', active_list

    if active_list:
        entries = user_manage_feeds.recalculate_entries(active_list, user, page, star)

    else:
        entries = []

    prefs = user_manage_feeds.get_user_prefs(user)
    print prefs

    return jsonify(success=True, e=entries, compressed_view=prefs)


@app.route('/sleep_data', methods=['POST'])
def sleep_data():

    print "sleeeeeeep, data"
    time.sleep(5)
    return jsonify(success=True)



@app.route('/get_unread_count', methods=['GET'])
def unread_count():

    user = g.user

    # Ok, so currently this is just using "feed_id", I probably actually want to send "uf_id"

    feed_id = request.args.get('feed', '', type=int)
    print feed_id

    result = user_manage_feeds.get_unread_count(feed_id, user)
    print result

    return jsonify(success=True, count=result)




