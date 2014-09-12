from flask import *
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user
from feedeater import flaskapp
from feedeater import lm, oid
from feedeater.config import configs as c
from feedeater.database.models import User
from feedeater.controller import user_manage_feeds, manage_users
from hashlib import md5

import logging
from feedeater import setup_logger
logger = logging.getLogger(__name__)
setup_logger(logger)
logger.setLevel(logging.DEBUG)


basedir = c.get('basedir')
app = Blueprint('index', __name__, static_folder=basedir+'/display/static',
                template_folder=basedir+'/display/templates')


@app.before_request
def before_request():
    logger.info("NEW MAIN.PY REQUEST:")
    g.user = current_user
    logger.info('user:    {0}'.format(g.user))


#####
# Functions for main page building:
#####

@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
@oid.loginhandler
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def build_index(page=1):

    logger.info('building page.')

    g.page = page
    user = g.user

    if user is None or not g.user.is_authenticated():
        user = manage_users.get_guest_user()
        login_user(user)

    g.hash = md5(user.email).hexdigest()

    # with either json, or render, this should actually be returning the user_entry table joined with entry
    # so we get a full list of user entries, tags, categories, stars, etc.
    return render_template("index.html", title='Home',
                           user=user,
                           providers=flaskapp.config['OPENID_PROVIDERS'],
                           prefs=1)


#####
# Functions for handling user login:
#####

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/f_login', methods=['GET', 'POST'])
@oid.loginhandler
def f_login():
    logger.info('I am attempting to login now...')
    try:
        url = request.form["url"]
    except Exception, e:
        logger.exception('exception exception exception!!!')
        return jsonify({'there were so many errors': str(e)})

    test = oid.try_login(url, ask_for=['nickname', 'email'])
    return test


@oid.after_login
def after_login(resp):

    logger.info('running after_login function now...')

    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('.build_index'))

    user = User.query.filter_by(email=resp.email).first()

    # if totally new user:
    if user is None:
        logger.debug('response: {0}'.format(resp))

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
    logger.info("successful logout for user: {0}".format(g.user))
    return redirect(url_for('.build_index'))






