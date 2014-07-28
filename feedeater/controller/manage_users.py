from feedeater.database.models import User, ROLE_USER
from feedeater import db


db_session = db.session


def add_user(resp):

    # some auths contain a nick, some don't.
    # if they don't, use first segment of email:
    nickname = resp.nickname
    if nickname is None or nickname == "":
        nickname = resp.email.split('@')[0]

    user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
    db.session.add(user)
    db.session.commit()

