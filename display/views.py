from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import Markup
from display import app, db, lm, oid
from forms import LoginForm
from app.models import User, ROLE_USER, ROLE_ADMIN, Entry
from app.config import configs as c



@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@oid.loginhandler
#@login_required
def index(page=1):
    user = g.user
    form = LoginForm(request.form)
    login_form = LoginForm()
    #get_entries = Entry.query.order_by(Entry.published.desc())  # move this to a function w/in models.
    # entries = get_entries[:30]

    if g.user.is_authenticated():
        entries = user.get_entries().paginate(page, c['POSTS_PER_PAGE'], False)
    else:
        entries = Entry.query.order_by(Entry.published.desc())[:10]

    if request.method == 'POST':

        if not form.validate():
            print 'maaaade it here:'
            user = User(nickname="Guest", email="guest@guest.com", role=0)
            return render_template("index.html", form=form, title='Home',
                                   user=user, entries=entries, providers=app.config['OPENID_PROVIDERS'],
                                   login_form=login_form)

        # user = form.valid_login(form, form.username.data)  # , form.password.data
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

    if user is None or not g.user.is_authenticated():
        print 'user is none!'
        user = User(nickname="Guest", email="guest@guest.com", role=0)

    if login_form.validate_on_submit():
        session['remember_me'] = login_form.remember_me.data
        return oid.try_login(login_form.openid.data, ask_for=['nickname', 'email'])

    return render_template("index.html", title='Home',
                           user=user, entries=entries, form=form,
                           providers=app.config['OPENID_PROVIDERS'],
                           login_form=login_form)






@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html',
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

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