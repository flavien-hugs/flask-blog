"""
Routes for user authentication.
"""

import os
import secrets

from flask import Blueprint, render_template, redirect, request, flash, url_for

from core.models import User
from core import db, bcrypt, login_manager
from core.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import login_user, logout_user, login_required, current_user


# Blueprint Configuration
auth = Blueprint("auth", __name__, url_prefix='/account/')


@auth.route("/register/", methods=['GET', 'POST'], strict_slashes=False)
@auth.route("/inscription/", methods=['GET', 'POST'], strict_slashes=False)
def registerPage():

    """
    User signup page.
    GET requests serve sign-up page.
    POST requests validate form & user creation.
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.homePage'))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(email=form.email.data, username=form.username.data)
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            db.session.add(user)
            db.session.commit()
            msg_success = f"""
                Hey <b>{username}</b>,
                votre compte a été créé ! Connectez-vous maintenant !
            """
            flash(msg_success, "success")
            return redirect(url_for('auth.loginPage'))
        except Exception as e:
            return f"Une erreur s'est produite: {e}"

    page_title = "Je m'inscris"

    return render_template(
        'pages/auth/register.html',
        page_title=page_title, form=form
    )


@auth.route("/login/", methods=['GET', 'POST'], strict_slashes=False)
@auth.route("/connexion/", methods=['GET', 'POST'], strict_slashes=False)
def loginPage():

    """
    Login page for registered users.
    GET requests serve Log-in page.
    POST requests validate and redirect user to dashboard.
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.homePage'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(
                    f"/account/{user.slug}/dashboard/"
                )

            flash("Combinaison nom d'utilisateur/mot de passe invalide.", "danger")
            return redirect(url_for('auth.loginPage'))
        except Exception as e:
            return f"Une erreur s'est produite: {e}"

    page_title = "Connexion"

    return render_template(
        'pages/auth/login.html',
        page_title=page_title, form=form
    )


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, extension = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + extension
    picture_path = os.path.join(auth.root_path, 'media/user/', picture_fn)
    form_picture.save(picture_path)

    return picture_fn


@auth.route('/account/me/update/account/', methods=['GET', 'POST'], strict_slashes=False)
@auth.route('/account/dashboard/update/account/', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def updateAccountPage():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        try:
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file

            current_user.email = form.email.data
            current_user.username = form.username.data
            db.session.commit()
            flash("Votre compte a été mise à jour avec succès.", "success")
            return redirect(url_for('auth.updateAccountPage'))
        except Exception as e:
            return f"Une erreur s'est produite: {e}"
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username

    user_picture = url_for(
        "static", filename=f"media/user/{current_user.image_file}"
    )

    page_title = "Modifier mon compte"

    return render_template(
        'pages/auth/settings.html',
        form=form,
        current_user=current_user,
        user_picture=user_picture,
        page_title=page_title,
    )


@auth.route('/logout/', strict_slashes=False)
@auth.route('/deconnexion/', strict_slashes=False)
@login_required
def logoutPage():
    """
    Logout page users.
    """
    logout_user()
    return redirect(url_for('main.homePage'))


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(int(user_id))
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('Vous devez être connecté pour voir cette page.')
    return redirect(url_for('auth.loginPage'))
