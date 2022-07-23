# main.forms.py

from flask import request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import(
    DataRequired, InputRequired, Email,
    ValidationError, Regexp
)

from ..models import Role, User, Contact


class SearchForm(FlaskForm):
    query = StringField('Rechercher un article ...', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class ContactForm(FlaskForm):
    fullname = StringField(
        "Nom & prénoms", validators=[DataRequired()]
    )
    email = StringField(
        'Adresse Email',
        validators=[
            DataRequired(),
            Email(message='Entrer une adresse email valide.')
        ]
    )
    subject = StringField("Sujet", validators=[DataRequired()])
    message = TextAreaField("Votre message", validators=[DataRequired()])
    submit = SubmitField("Envoyer")
