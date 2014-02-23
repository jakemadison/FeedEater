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
app = Blueprint('entries', __name__, static_folder=basedir+'/display/static',
                template_folder=basedir+'/display/templates')

@app.before_request
def before_request():
    g.user = current_user

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
    result = user_manage_feeds.change_star_state(user, entryid)
    print result

    return jsonify({"result": result})