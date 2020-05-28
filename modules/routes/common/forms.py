from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Length

from modules.routes.utils.custom_fields import InlineSubmitField


class LoginForm(FlaskForm):
    email = EmailField("Enter Email", validators=[
        InputRequired("An email address is required"),
        Length(min=1, max=255, message="Something went wrong, please try again.")
    ], render_kw={"class": "form-control"})

    password = PasswordField('Enter Password', validators=[
        InputRequired("A password is required"),
        Length(min=1, max=255, message="Something went wrong, please try again.")
    ], render_kw={"class": "form-control"})

    loginBtn = InlineSubmitField("Login", btn_text="Login", render_kw={"class": "btn btn-block btn-sm grey lighten-2"})

    rememberMe = BooleanField("Remember Me", render_kw={"class":"custom-control-input"})