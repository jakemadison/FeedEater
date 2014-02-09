from flask.ext.wtf import Form, SubmitField
from wtforms import TextField, BooleanField
from wtforms.validators import Required, url, ValidationError


class LoginForm(Form):
    openid = TextField('openid', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class AddFeedForm(Form):
    feed = TextField("feed", validators=[Required("Feed Url is Required"), url("Not a recognized url")])
    submit = SubmitField("Add")