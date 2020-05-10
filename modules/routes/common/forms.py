from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired,Length,AnyOf

class LoginForm(FlaskForm):
    email = EmailField("Enter Email",validators=[InputRequired()])
    password = PasswordField('Enter Password',validators=[InputRequired()])