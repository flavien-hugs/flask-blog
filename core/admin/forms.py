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

from ..models import Role, User
from flask_ckeditor import CKEditorField


GENDER_CHOICES = [
    ('Mr', 'Mr'),
    ('Mme', 'Mme'),
    ('Mlle', 'Mlle')
]


class EditProfileAdminForm(FlaskForm):
    role = SelectField('Role', coerce=int)
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

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_username(self, username):
        if (
            username.data != current_user.username
            and User.query.filter_by(username=username.data).first()
        ):
            raise ValidationError(
                f"""
                    Cet nom '{username.data}' d'utilisateur est déjà utilisé.
                    Veuillez choisir un autre nom !
                """
            )

    def validate_email(self, email):
        if(
            email.data != current_user.email
            and User.query.filter_by(email=email.data).first()
        ):
            raise ValidationError(
                f"""
                    Cet adresse '{email.data}' est déjà utilisé.
                    Veuillez choisir un autre nom !
                """
            )
