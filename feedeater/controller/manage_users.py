from feedeater.database.models import User, ROLE_USER
from feedeater import db


db_session = db.session


def add_user(resp):

    # some auths contain a nick, some don't, use first portion of email if not
    nickname = resp.nickname
    if nickname is None or nickname == "":
        nickname = resp.email.split('@')[0]

    user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
    db.session.add(user)
    db.session.commit()


def get_guest_user():
    qry = db_session.query(User).filter(User.email == 'guest@noemail.com')
    u = qry.first()
    print u, dir(u), u.nickname
    return u