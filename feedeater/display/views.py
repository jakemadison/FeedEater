from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import Markup
from feedeater import flaskapp as app
from feedeater import lm, oid
from feedeater.display.forms import LoginForm, AddFeedForm
from feedeater.config import configs as c
from feedeater.database.models import User, ROLE_USER, Entry
from feedeater.controller import user_manage_feeds
import sys
from feedeater.controller import FeedGetter


@app.route('/tags', methods=['POST'])
def get_json():

    user = g.user
    tag_text = request.form['tagtext']
    tag_id = request.form['tagid']

    print tag_text, tag_id

    if g.user.is_authenticated():
        tags = user_manage_feeds.get_user_tags(user)
    else:
        return redirect(request.args.get('next') or url_for('index'))

    return jsonify(title='Home', tags=tags)




@app.route('/togglefeed', methods=['POST'])
def toggle_feed():

    # this should just update DB to change active state
    ufid = request.form['ufid']
    print ufid
    result = True
    return jsonify({'ufid': ufid, 'result': result})



@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user




def return_a_page():
    user = g.user
    form = LoginForm(request.form)
    login_form = LoginForm()






@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@oid.loginhandler
#@login_required
def index(page=1):

    print app
    print __name__
    #print dir(app)

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

    if request.method == 'POST':
        if not form.validate():
            print 'maaaade it here:'
            user = User(nickname="Guest", email="guest@guest.com", role=0)
            return render_template("index.html", form=form, title='Home',
                                   user=user, entries=entries, providers=app.config['OPENID_PROVIDERS'],
                                   login_form=login_form, subs=sl)  # SL not defined yet...

        if not user:
            print 'made it here...'
            form.errors = True
            form.error_messages = ["The login details provided are not correct."]
            return render_template("index.html", form=form, title='Home', user=user,
                                   entries=entries, providers=app.config['OPENID_PROVIDERS'],
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

    else:
        print "}}}retrieving sublist here...."
        sub_list = user_manage_feeds.get_user_feeds(user)

    print user

    sl = sub_list['feed_data']  # sl needs to send count data as well. or send it from entries?


    return render_template("index.html", title='Home',
                           user=user, entries=entries, form=form,
                           providers=app.config['OPENID_PROVIDERS'],
                           login_form=login_form, subs=sl, add_feed_form=add_feed_form)


@app.route('/add_feed', methods=['POST'])
def add_feed():
    print "        ]]]]] add_feed has been activated"
    add_feed_form = AddFeedForm(csrf_enabled=False)
    user = g.user
    form = LoginForm()
    entries = None

    if not add_feed_form.validate_on_submit():
        print "add form has not validated"
        print 'form errors: ', add_feed_form.feed.errors

        for error in add_feed_form.feed.errors:
            flash(error, 'error')

        return redirect(request.args.get('next') or url_for('index'))

    else:
        print "    add form HAS validated!"
        print "adding user feed: ", add_feed_form.feed.data
        result = user_manage_feeds.add_user_feed(user, add_feed_form.feed.data)

        if result == "already_associated":
            flash("Already Subscribed  :)", "info")

        elif result == "success":
            flash("Successfully added new feed  :D", "info")

        elif result == "error_adding_feed":
            flash("Unknown error adding feed  :o", "error")

        elif result == "no_feed_found":
            flash("No rss feed found at that url  :(", "error")

        return redirect(request.args.get('next') or url_for('index'))



# temp route to refresh from front end.
@app.route('/refresh')
def refresh_feeds():
    user = g.user
    x = user_manage_feeds.get_user_feeds(user)
    send_feed = [f['url'] for f in x['feed_data']]  # change this...
    FeedGetter.main(send_feed)

    return redirect(request.args.get('next') or url_for('index'))


@app.route('/change_active')
def change_active():

    print "----- entering change active"
    ufid = request.args.get('ufid')
    active = request.args.get('a')
    user_manage_feeds.update_is_active(ufid, active)
    print 'finished change_active.'

    # this part isn't working for remember page:
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/favs/')
def favs():
    print "holy shit... it's not THAT easy.. is it??"

    # I feel like this redirection business is causing page loading that
    # it does not need to, and so overall app slowdown.
    # except that feed changes, do need to be dealt with somehow

    return redirect(url_for('index'))


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


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('index'))

    user = User.query.filter_by(email=resp.email).first()

    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))