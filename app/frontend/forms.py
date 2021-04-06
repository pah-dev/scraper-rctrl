from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms import validators
from wtforms.fields.core import BooleanField, FieldList, FormField, IntegerField, SelectField
from wtforms.fields.simple import FileField, HiddenField, TextField
from wtforms.validators import DataRequired


class RunForm(FlaskForm):
    id_org = SelectField('Organization', [DataRequired()], choices=[("actc", "ACTC"), ("apat", "APAT"), ("aptp", "APTP"), (
        "auvo", "AUVO"), ("carx", "CARX"), ("cur", "CUR"), ("gpu", "GPU"), ("mss", "MSS"), ("tc", "TC"), ("tr", "TR")])
    year = IntegerField('Year')
    manual = BooleanField('Manual')
    org = HiddenField('org')
    submit = SubmitField('create')
