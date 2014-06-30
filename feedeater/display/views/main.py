from flask import *
from flask import render_template, flash, redirect, session, url_for, request, g  # , jsonify
from flask.ext.login import login_user, logout_user, current_user  # , login_required
from feedeater import flaskapp
from feedeater import lm, oid
from feedeater.display.forms import LoginForm, AddFeedForm
from feedeater.config import configs as c
from feedeater.database.models import User  # , ROLE_USER, Entry, UserEntry
from feedeater.controller import user_manage_feeds, manage_users
#from flask import Markup
#import sys
#from feedeater.controller import FeedGetter

# This module should handle the main rendering as well as login/out and authorization

basedir = c.get('basedir')
app = Blueprint('index', __name__, static_folder=basedir+'/display/static',
                template_folder=basedir+'/display/templates')


@app.before_request
def before_request():
    print "\n\n\n- NEW MAIN.PY REQUEST:"
    g.user = current_user
    print 'user:    ', g.user


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


# @login_required
@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@oid.loginhandler
def build_index(page=1):

    g.page = page
    user = g.user

    form = LoginForm(request.form)
    login_form = LoginForm()

    add_feed_form = AddFeedForm(csrf_enabled=False)  # this should maybe be true... :/

    if user is None or not g.user.is_authenticated():
        user = user_manage_feeds.get_guest_user()
        login_user(user)

    # with either json, or render, this should actually be returning the user_entry table joined with entry
    # so we get a full list of user entries, tags, categories, stars, etc.
    return render_template("index.html", title='Home',
                           user=user, form=form,
                           providers=flaskapp.config['OPENID_PROVIDERS'],
                           login_form=login_form, add_feed_form=add_feed_form, prefs=1)


# this function is now handling login via js request:
@app.route('/f_login', methods=['GET', 'POST'])
@oid.loginhandler
def f_login():
    print 'attempting to login now...'

    url = request.form["url"]
    return oid.try_login(url, ask_for=['nickname', 'email'])


@oid.after_login
def after_login(resp):

    print 'running after_login function now...'

    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('.build_index'))

    user = User.query.filter_by(email=resp.email).first()

    # if totally new user:
    if user is None:
        print resp
        print dir(resp)

        manage_users.add_user(resp)
        user = User.query.filter_by(email=resp.email).first()

    remember_me = False

    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)

    login_user(user, remember=remember_me)

    return redirect(request.args.get('next') or url_for('.build_index'))


@app.route('/logout')
def logout():
    logout_user()
    print "successful logout for user: ", g.user
    return redirect(url_for('.build_index'))






