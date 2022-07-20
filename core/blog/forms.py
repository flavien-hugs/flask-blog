from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length
from wtforms import StringField, SubmitField

from flask_ckeditor import CKEditorField


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
