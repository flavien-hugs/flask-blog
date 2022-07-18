"""
Routes for user authentication.
"""

import os
import uuid
import secrets

from flask import(
    Blueprint, render_template, redirect, request,
    flash, url_for
)

from core.models import User
from core import db, bcrypt, login_manager, mail
from core.forms import(
    RegistrationForm, LoginForm, UpdateAccountForm,
    ForgotPasswordForm, ResetPasswordForm
)
from flask_mail import Message
from PIL import Image
from flask_login import(
    login_user, logout_user, login_required,
    current_user
)


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
            user = User(gender=form.gender.data, email=form.email.data.lower(), username=form.username.data)
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            db.session.add(user)
            db.session.commit()
            msg_success = f"""
                Hey {form.username.data},
                votre compte a été créé ! Connectez-vous maintenant !
            """
            flash(msg_success, "success")
            return redirect(url_for('auth.loginPage'))
        except Exception as e:
            return f"Une erreur s'est produite: {e}"

    page_title = "Je m'inscris"

    return render_template(
        'auth/register.html',
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
        user = User.query.filter_by(email=form.email.data.lower()).first()
        try:
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                if next_page is None or not next_page.startswith('/'):
                    next_page = url_for('main.dashboardPage')
                return redirect(next_page)

                # return redirect(next_page) if next_page else redirect(url_for('main.dashboardPage'))

            flash("Combinaison nom d'utilisateur/mot de passe invalide.", "danger")
            return redirect(url_for('auth.loginPage'))
        except Exception as e:
            return f"Une erreur s'est produite: {e}"

    page_title = "Connexion"

    return render_template(
        'auth/login.html',
        page_title=page_title, form=form
    )


def send_reset_email(user):
    token = user.generate_reset_token()
    msg = Message(
        "Demande de réinitialisation de mot de passe",
        sender='noreply@unsta.com',
        recipients=[user.email.lower()]
    )
    msg.body = f'''Pour réinitialiser votre mot de passe, visitez le lien suivant:
    {url_for('auth.resetTokenPage', token=token, _external=True)}.

    Si vous n'avez pas fait cette demande, ignorez simplement cet e-mail et aucun changement ne sera effectué.
    '''
    mail.send(msg)


@auth.route("/reset/password/", methods=['POST'], strict_slashes=False)
def resetRequestPage():
    if current_user.is_authenticated:
        return redirect(url_for('main.homePage'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        send_reset_email(user)
        flash(
            "Un courriel a été envoyé avec les instructions pour réinitialiser votre mot de passe.",
            'info'
        )
        return redirect(url_for('auth.loginPage'))

    page_title = 'Réinitialiser votre mot de passe'
    return render_template('auth/resetpwd.html', page_title=page_title, form=form)


@auth.route("/reset/password/<token>/", methods=['GET', 'POST'], strict_slashes=False)
def resetTokenPage(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.homePage'))

    user = User.verify_reset_token(token)
    if user is not None:
        flash("Ce jeton est invalide ou a expiré.", 'warning')
        return redirect(url_for('auth.resetRequestPage'))

    form = ResetPasswordForm()
    try:
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Votre mot de passe a été mise à jour avec succès !", "success")
        return redirect(url_for('auth.loginPage'))
    except Exception as e:
        return f"Une erreur s'est produite: {e}"

    page_title = 'Changer votre mot de passe'
    return render_template(
        'auth/changepwd.html',
        page_title=page_title,
        form=form
    )


def save_profile_picture(picture):
    random_hex = secrets.token_hex(8)
    _, extension = os.path.splitext(picture.filename)
    picture_fn = random_hex + extension
    picture_path = os.path.join(auth.root_path, 'static/media/user/', picture_fn)

    output_size = (256, 256)
    thumb = Image.open(picture)
    thumb.thumbnail(output_size)
    thumb.save(picture_path)

    return picture_fn


@auth.route('/account/me/update/account/', methods=['GET', 'POST'], strict_slashes=False)
@auth.route('/account/dashboard/update/account/', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def updateAccountPage():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        try:
            if form.picture.data:
                picture_file = save_profile_picture(form.picture.data)
                current_user.image_file = picture_file

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
        form.website.data = current_user.website
        form.username.data = current_user.username
        form.biography.data = current_user.biography

    page_title = "Modifier mon compte"

    return render_template(
        'auth/settings.html',
        form=form,
        current_user=current_user,
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
