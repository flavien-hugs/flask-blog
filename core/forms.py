# core.forms.py

from flask_login import current_user

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import(
    DataRequired, InputRequired, Email, Length, EqualTo, ValidationError
)
from core.models import User


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
        validators=[
            DataRequired(),
            Email(message='Entrer une adresse email valide.')
        ]
    )
    password = PasswordField(
        'Mot de passe',
        validators=[
            InputRequired(),
            Length(
                min=6, max=18,
                message='Choisissez un mot de passe plus fort.'
            )
        ]
    )
    confirm_password = PasswordField(
        'Confirmer le mot de passe',
        validators=[
            InputRequired(),
            EqualTo(
                'password',
                message='Les deux mots de passe ne correspondent pas.'
            ),
        ]
    )
    submit = SubmitField("Je m'inscris")


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                f"""
                Cet nom '{username.data}' d'utilisateur est déjà utilisé.
                Veuillez choisir un autre nom !
                """
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                f"""
                Cet adresse '{email.data}' est déjà utilisé.
                Veuillez choisir un autre nom !
                """
            )


class LoginForm(FlaskForm):
    email = StringField(
        'Adresse Email',
        validators=[
            DataRequired(),
            Email(message='Entrer une adresse email valide.')
        ]
    )
    password = PasswordField(
        'Mot de passe',
        validators=[DataRequired()]
    )
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')


class UpdateAccountForm(FlaskForm):
    username = StringField(
        'Nom & prénoms',
        validators=[
            DataRequired(),
            Length(min=2, max=50)
        ]
    )
    email = StringField(
        'Adresse Email',
        validators=[
            DataRequired(),
            Email(message='Entrer une adresse email valide.')
        ]
    )
    submit = SubmitField("Mettre à jour mon compte")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    f"""
                    Cet nom '{username.data}' d'utilisateur est déjà utilisé.
                    Veuillez choisir un autre nom !
                    """
                )

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    f"""
                    Cet adresse '{email.data}' est déjà utilisé.
                    Veuillez choisir un autre nom !
                    """
                )
