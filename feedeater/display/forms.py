from flask.ext.wtf import Form, SubmitField
from wtforms import TextField, BooleanField, RadioField
from wtforms.validators import Required, url, ValidationError


class LoginForm(Form):
    openid = TextField('openid', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class AddFeedForm(Form):
    feed = TextField("feed", validators=[Required("Feed Url is Required"), url("Not a recognized url")])
    submit = SubmitField("Add")


class EditFeedAttributes(Form):
    category = TextField("category")
    update_frequency = RadioField("update frequency", choices=[('never', 'never update'),
                                                               ('seldom', 'sometimes update'),
                                                               ('regular', 'same as it ever was'),
                                                               ('often', 'frequently update')])
    save = SubmitField("Save")