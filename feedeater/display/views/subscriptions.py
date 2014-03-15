from flask import *
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import Markup
from feedeater import flaskapp
from feedeater import lm, oid
from feedeater.display.forms import LoginForm, AddFeedForm
from feedeater.config import configs as c
from feedeater.database.models import User, ROLE_USER, Entry, UserEntry
from feedeater.controller import user_manage_feeds
import sys
from feedeater.controller import FeedGetter


basedir = c.get('basedir')
app = Blueprint('subscriptions', __name__, static_folder=basedir+'/display/static',
                template_folder=basedir+'/display/templates')


# all of these methods need to now be json instead of redirect. fun.

def before_blueprint_request():
    g.user = current_user

app.before_request(before_blueprint_request)


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


@app.route('/activatecategory', methods=['POST'])
def activate_category():

    print 'entering activate_category function'
    user = g.user
    print user

    cat = request.form['catname']
    user_manage_feeds.activate_category(user, cat)
    # return redirect(request.args.get('next') or url_for('index'))
    return jsonify(success=True)



@app.route('/onefeedonly', methods=['POST'])
def one_feed_only():
    print 'changing to one feed only'

    uf_id = request.form['uf_id']
    user = g.user
    user_manage_feeds.single_active(user, uf_id)

    return jsonify(success=True)


@app.route('/allfeeds', methods=['POST'])
def show_all_feeds():

    print "entered all feeds method==========================="
    user = g.user
    user_manage_feeds.all_active(user)
    # return redirect(request.args.get('next') or url_for('index'))
    return jsonify(success=True)


@app.route('/change_active', methods=['POST'])
def change_active():

    print "----- entering change active"
    uf_id = request.form['uf_id']
    user_manage_feeds.update_is_active(uf_id)

    print 'finished change_active.'

    return jsonify(success=True)



@app.route('/refreshfeeds')
def ref_feeds():
    user = g.user
    user_manage_feeds.main(user)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/unsubscribe')
def unsubscribe():
    print "removing feed from user_feeds"
    user = g.user
    feedid = request.args.get('ufid')
    result = user_manage_feeds.remove_user_feed(user, feedid)

    if result == "successfully deleted":
        flash("Successfully removed  :D", "info")
    elif result == "error_deleting_feed":
        flash("Unknown error removing feed  :(", "error")
    elif result == "feed_id not found":
        flash("Feed Id Not found  :(", "error")

    print "finished removing feed"

    return redirect(request.args.get('next') or url_for('index'))


# this needs to be jsonifyied: or at least for the invalid responses...
@app.route('/add_feed', methods=['POST'])
def add_feed():

    print "........]]]]] add_feed has been activated"

    # add_feed_form = AddFeedForm(csrf_enabled=False)
    user = g.user

    data = request.form["data"]

    print '...............', data

    # this doesn't check for bad input..
    # need to validate if URL / if empty here

    result = user_manage_feeds.add_user_feed(user, data)

    print result

    if result == "already_associated":
        msg = "Already Subscribed  :)"
        category = "info"

    elif result == "success":
        msg = "Successfully added new feed  :D"
        category = "success"

    elif result == "error_adding_feed":
        msg = "Unknown error adding feed  :o"
        category = "error"

    elif result == "no_feed_found":
        msg = "No rss feed found at that url  :("
        category = "error"
    else:
        msg = "Unknown error ????"
        category = "error"
    return jsonify(msg=msg, category=category)

        # return redirect(url_for('index.build_index'))


@app.route('/starred_only', methods=['POST'])
def only_starred():
    user = g.user

    # this should run recalc entries.. but with all feeds considered active (?)
    # or should you only see starred entries from active ones?
    # anyways, either way, just send starred_only=True (default to false on sig
    # of function) and then just add an extra where clause for UserEntry.starred = True.

    # result = user_manage_feeds.recalculate_entries()

    return False