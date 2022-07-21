# main.forms.py

from flask import request

from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField

from ..models import Role, User


class SearchForm(FlaskForm):
    query = StringField(
        'Rechercher un article ...',
        validators=[DataRequired()]
    )
    submit = SubmitField('rechercher')

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)
