from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Length, AnyOf


class LoginForm(FlaskForm):
    email = EmailField("Enter Email", validators=[
        InputRequired("An email address is required"),
        Length(min=1, max=255, message="Something went wrong, please try again.")
    ])
    password = PasswordField('Enter Password', validators=[
        InputRequired("A password is required"),
        Length(min=1, max=255, message="Something went wrong, please try again.")
    ])
