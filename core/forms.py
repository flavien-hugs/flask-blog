# core.forms.py

from flask_wtf import FlaskForm
from wtforms.validators import(
    DataRequired, Email, Length, EqualTo
)
from wtforms import(
    StringField, PasswordField, SubmitField,
    BooleanField
)


class RegistrationForm(FlaskForm):
    username = StringField(
        'Nom & prénoms',
        validators=[
            DataRequired(),
            Length(min=2, max=50)
        ]
    )
    email = StringField(
        'Adresse Email',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Mot de passe',
        validators=[DataRequired()]
    )
    confirm_password = PasswordField(
        'Confirmer le mot de passe',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField("Je m'inscris")


class LoginForm(FlaskForm):
    email = StringField(
        'Adresse Email',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Mot de passe',
        validators=[DataRequired()]
    )
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')
