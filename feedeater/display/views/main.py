from flask import *
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import Markup
from feedeater import flaskapp
from feedeater import lm, oid
from feedeater.display.forms import LoginForm, AddFeedForm
from feedeater.config import configs as c
from feedeater.database.models import User, ROLE_USER, Entry, UserEntry
from feedeater.controller import user_manage_feeds, manage_users
import sys
from feedeater.controller import FeedGetter

# This module should handle the main rendering & paging functions as well as login/out and authorization


basedir = c.get('basedir')
app = Blueprint('index', __name__, static_folder=basedir+'/display/static',
                template_folder=basedir+'/display/templates')


@app.before_request
def before_request():
    print "\n\n\nNEW MAIN.PY REQUEST:"
    g.user = current_user
    # print "\n        ->user: ", g.user, dir(g.user), g.user.nickname, g.user.id, "\n\n..."


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

# @login_required
@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@oid.loginhandler
def build_index(page=1):

    # really need to decide whether this is all going to be ajax/json
    # or if we want to use built in flask pagination..

    # print app

    # will this work??
    g.page = page


    print __name__
    #print dir(app)
    user = None
    user = g.user
    # print "\n        ->user: ", user, dir(user), user.nickname, "\n\n..."
    form = LoginForm(request.form)
    login_form = LoginForm()
    prefs = None

    add_feed_form = AddFeedForm(csrf_enabled=False)

    if g.user.is_authenticated():
        print '!!!!! - retrieving entries from is_authenticated call...'
        entries = user.get_entries_new().paginate(page, c['POSTS_PER_PAGE'], False)
        prefs = user_manage_feeds.get_user_prefs(user)

        # user_entry_list = user_manage_feeds.get_user_entry_records(user, entries)
        # okay, so now I just need to add these entries to our entry list...

    else:
        print 'thiiiisssss..... is failing. move all this to user_man_feeds? ...actually, '
        print 'sub_list returns a list of feedIds.. can just use those to get entries..'
        entries = Entry.query.order_by(Entry.published.desc())[:10]
        sub_list = user_manage_feeds.get_guest_feeds()
        sl = sub_list['feed_data']
        cats = []

    if request.method == 'POST':
        user = g.user
        if not form.validate():
            print 'maaaade it here:'
            #user = User(nickname="Guest", email="guest@guest.com", role=0)
            # return render_template("index.html", form=form, title='Home',
            #                        user=user, entries=entries, providers=flaskapp.config['OPENID_PROVIDERS'],
            #                        login_form=login_form, subs=sl)  # SL not defined yet...

        if not user:
            print 'made it here...'
            form.errors = True
            form.error_messages = ["The login details provided are not correct."]
            return render_template("index.html", form=form, title='Home', user=user,
                                   entries=entries, providers=flaskapp.config['OPENID_PROVIDERS'],
                                   login_form=login_form)

        print '!!!!yesssssssssssss!!!!'
        login_user(user)
        session['logged_in'] = True
        # flash("Logged in successfully.")

    if login_form.validate_on_submit():
        session['remember_me'] = login_form.remember_me.data
        return oid.try_login(login_form.openid.data, ask_for=['nickname', 'email'])

    if user is None or not g.user.is_authenticated():
        print 'user is none!'
        user = User(nickname="Guest", email="guest@guest.com", role=0)
        sub_list = user_manage_feeds.get_guest_feeds()
        cats = []

    else:
        print "}}}retrieving sublist here...."
        # something here is causing OS to kill with OOM error.

        sub_list = user_manage_feeds.get_user_feeds(user)

        print "sublist received"
        # print sub_list

        cats = sub_list['cat_list']
        cats = sorted(cats)
        # print "cats cats cats ------- ", cats

        print "categories loaded and sorted"

        #print "================>", cats


    #print user

    sl = sub_list['feed_data']  # sl needs to send count data as well. or send it from entries?

    print "sl loaded"
    # print sl

    # wow, this was causing an OOM error apparently.
    # test_entries = user.get_userentries().first()
    # print '------->', test_entries
    # jsonify and paginate, easy as that!
    # print dir(test_entries.remote_id)


    print "\n"

    # test = user_manage_feeds.test_get_entires(user)
    # for each in test:
    #     print each

    if not prefs:
        prefs = {"compressed_view": False}


    print "finished all loading.. rendering template now."

    # with either json, or render, this should actually be returning the user_entry table joined with entry
    # so we get a full list of user entries, tags, categories, stars, etc.
    return render_template("index.html", title='Home',
                           user=user, entries=entries, form=form,
                           providers=flaskapp.config['OPENID_PROVIDERS'],
                           login_form=login_form, subs=sl, add_feed_form=add_feed_form,
                           cats=cats, prefs=prefs)


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('.build_index'))
    form = LoginForm()

    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=flaskapp.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('.build_index'))

    user = User.query.filter_by(email=resp.email).first()

    # if totally new user
    if user is None:
        print resp
        print dir(resp)

        manage_users.add_user(resp)


    remember_me = False

    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)

    login_user(user, remember=remember_me)

    return redirect(request.args.get('next') or url_for('.build_index'))


@app.route('/logout')
def logout():
    logout_user()
    print "successful logout"
    print g.user
    return redirect(url_for('.build_index'))



@app.route('/change_view', methods=['POST'])
def change_view():

    user = g.user
    print 'user: ', user.nickname, user.id
    user_manage_feeds.changeview(user)

    print "done! changeview!"

    return jsonify(success=True)



@app.route('/_json', methods=['GET', 'POST'])
def json_index(page=1):

    # ok, i think i have a handle on this then. these view functions need to be
    # divided. on one side, are all functions that return static/refresh data
    # those need to use "render template". the other group needs to be json
    # and those methods do not refresh, but do make server calls.

    # print app
    print __name__
    user = None

    user = g.user
    form = LoginForm(request.form)
    login_form = LoginForm()

    add_feed_form = AddFeedForm(csrf_enabled=False)

    if g.user.is_authenticated():
        print '!!!!! - retrieving entries from is_authenticated call...'
        entries = user.get_entries_new().paginate(page, c['POSTS_PER_PAGE'], False)

    else:
        print 'thiiiisssss..... is failing. move all this to user_man_feeds? ...actually, '
        print 'sub_list returns a list of feedIds.. can just use those to get entries..'
        entries = Entry.query.order_by(Entry.published.desc())[:10]
        sub_list = user_manage_feeds.get_guest_feeds()
        sl = sub_list['feed_data']
        cats = []

    if request.method == 'POST':
        if not form.validate():
            print 'maaaade it here:'
            user = User(nickname="Guest", email="guest@guest.com", role=0)
            return render_template("index.html", form=form, title='Home',
                                   user=user, entries=entries, providers=flaskapp.config['OPENID_PROVIDERS'],
                                   login_form=login_form, subs=sl)  # SL not defined yet...

        if not user:
            print 'made it here...'
            form.errors = True
            form.error_messages = ["The login details provided are not correct."]
            return render_template("index.html", form=form, title='Home', user=user,
                                   entries=entries, providers=flaskapp.config['OPENID_PROVIDERS'],
                                   login_form=login_form)

        print '!!!!yesssssssssssss!!!!'
        login_user(user)
        session['logged_in'] = True
        flash("Logged in successfully.")

    if login_form.validate_on_submit():
        session['remember_me'] = login_form.remember_me.data
        return oid.try_login(login_form.openid.data, ask_for=['nickname', 'email'])

    if user is None or not g.user.is_authenticated():
        print 'user is none!'
        user = User(nickname="Guest", email="guest@guest.com", role=0)
        sub_list = user_manage_feeds.get_guest_feeds()
        cats = []

    else:
        print "}}}retrieving sublist here...."
        sub_list = user_manage_feeds.get_user_feeds(user)
        cats = sub_list['cat_list']
        cats = sorted(cats)

        print "================>", cats


    print user

    sl = sub_list['feed_data']  # sl needs to send count data as well. or send it from entries?

    # print sl

    test_entries = user.get_userentries().first()
    print '------->', test_entries
    # jsonify and paginate, easy as that!
    # print dir(test_entries.remote_id)

    print entries
    print dir(entries)
    json_entries = {}
    for k, each in enumerate(entries.items):
        print jsonify(each.json_entry())



    print "\n"


    # return jsonify({"subs": sl, "entries": entries})
    return jsonify({"subs": sl})
    # with either json, or render, this should actually be returning the user_entry table joined with entry
    # so we get a full list of user entries, tags, categories, stars, etc.

    # return render_template("index.html", title='Home',
    #                        user=user, entries=entries, form=form,
    #                        providers=app.config['OPENID_PROVIDERS'],
    #                        login_form=login_form, subs=sl, add_feed_form=add_feed_form,
    #                        cats=cats)


@app.route('/json.html')
def json_index():
    return render_template("jsonindex.html")