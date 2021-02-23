# model.py
from wtforms import SubmitField, BooleanField, StringField, PasswordField, validators
from flask_wtf import Form
class RegForm(Form):
    name_first = StringField('First Name')
    name_last = StringField('Last Name')
    submit = SubmitField('Submit')
