from flask_wtf import Form
from wtforms.fields.core import BooleanField, DateField, DateTimeField
from wtforms.fields.core import DecimalField, FloatField, IntegerField
from wtforms.fields.simple import FileField, SubmitField, TextField
from wtforms.validators import Required


class SignupForm(Form):
    name = TextField(u'Your name')
    password = TextField(u'Your favorite password')
    email = TextField(u'Your email address')
    birthday = DateField(u'Your birthday')

    a_float = FloatField(u'A floating point number')
    a_decimal = DecimalField(u'Another floating point number')
    a_integer = IntegerField(u'An integer')

    now = DateTimeField(u'Current time',
                        description='...for no particular reason')
    sample_file = FileField(u'Your favorite file')
    eula = BooleanField(u'I did not read the terms and conditions',
                        validators=[Required('You must agree to not agree!')])

    submit = SubmitField(u'Signup')
