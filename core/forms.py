# core.forms.py

from flask_login import current_user

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import(
    DataRequired, InputRequired, Email, Length, EqualTo,
    ValidationError, Regexp
)
from wtforms import(
    StringField, PasswordField, SubmitField,
    BooleanField, SelectField
)

from core.models import User
from flask_ckeditor import CKEditorField


GENDER_CHOICES = [
    ('Mr', 'Mr'),
    ('Mme', 'Mme'),
    ('Mlle', 'Mlle')
]


class RegistrationForm(FlaskForm):
    gender = SelectField(
        'Civilité',
        choices=GENDER_CHOICES,
        validators=[DataRequired()]
    )
    username = StringField(
        'Nom & prénoms',
        validators=[
            DataRequired(),
            Length(min=2, max=50),
            Regexp(
                '^[A-Za-z][A-Za-z0-9_.]*$', 0,
                "Les noms d'utilisateur ne doivent comporter que des lettres, des chiffres, des points ou des symboles." 'underscores'
            )
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
    remember = BooleanField(
        'Se souvenir de moi',
    )
    submit = SubmitField('Se connecter')


class UpdateAccountForm(FlaskForm):
    gender = SelectField(
        'Civilité',
        choices=GENDER_CHOICES,
        validators=[DataRequired()]
    )
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
    biography = CKEditorField(
        'Description',
        validators=[DataRequired()]
    )
    website = StringField("Votre site web")
    picture = FileField(
        'Photo de profile',
        validators=[FileAllowed(['jpg', 'png'])]
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


class PostForm(FlaskForm):
    title = StringField(
        "Titre de l'article", validators=[DataRequired()]
    )
    content = CKEditorField(
        "Qu'est-ce qui vous préoccupe à ce sujet ?",
        validators=[DataRequired()]
    )
    picture = FileField(
        "Image d'illustration",
        validators=[FileAllowed(['jpg', 'png'])]
    )
    submit = SubmitField("Publier l'article")


class RequestPasswordResetForm(FlaskForm):
    email = StringField(
        'Adresse Email',
        validators=[
            DataRequired(),
            Email(message='Entrer une adresse email valide.')
        ]
    )
    submit = SubmitField('Envoyer le lien de réinitialisation')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                f"""
                Il n'y a pas de compte avec cet email '{email.data}'.
                Veuillez-vous inscrire.
                """
            )


class ResetPasswordForm(FlaskForm):
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
    submit = SubmitField('Modifier de mot de passe')
