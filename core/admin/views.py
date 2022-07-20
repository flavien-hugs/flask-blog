import os
import secrets

from flask import(
    render_template, redirect, request,
    flash, url_for, current_app
)

from . import admin
from ..models import db, Role, User
from .forms import EditProfileAdminForm
from ..decorators import is_admin_required

from PIL import Image
from flask_login import login_required, current_user


def save_profile_picture(picture):
    random_hex = secrets.token_hex(8)
    _, extension = os.path.splitext(picture.filename)
    picture_fn = random_hex + extension
    picture_path = os.path.join(
        auth.root_path, 'static/media/user/', picture_fn)

    output_size = (256, 256)
    thumb = Image.open(picture)
    thumb.thumbnail(output_size)
    thumb.save(picture_path)

    return picture_fn


@admin.route('/dashboard/', methods=['GET', 'POST'], strict_slashes=False)
@login_required
@is_admin_required
def editAdminDashboardPage():
    form = EditProfileAdminForm()
    if form.validate_on_submit():
        try:
            if form.picture.data:
                picture_file = save_profile_picture(form.picture.data)
                current_user.image_file = picture_file

            current_user.role = Role.query.get(form.role.data)
            current_user.email = form.email.data.lower()
            current_user.website = form.website.data
            current_user.username = form.username.data
            current_user.biography = form.biography.data
            db.session.add(current_user._get_current_object())
            db.session.commit()
            flash("Votre compte a été mise à jour avec succès.", "success")
            return redirect(url_for('auth.updateAccountPage'))
        except Exception as e:
            return f"Une erreur s'est produite: {e}"
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.role.data = current_user.role_id
        form.website.data = current_user.website
        form.username.data = current_user.username
        form.biography.data = current_user.biography

    page_title = "Compte Administrateur"

    return render_template(
        'admin/settings.html',
        form=form,
        current_user=current_user,
        page_title=page_title,
    )
