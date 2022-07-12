"""
Routes for user authentication.
"""

from flask import Blueprint, render_template, redirect, request, flash, url_for

from core.models import User
from core import db, bcrypt, login_manager
from core.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user


# Blueprint Configuration
auth = Blueprint("auth", __name__)


@auth.route("/account/register/", methods=['GET', 'POST'])
@auth.route("/account/inscription/", methods=['GET', 'POST'])
def registerPage():

    """
    User sign-up page.
    GET requests serve sign-up page.
    POST requests validate form & user creation.
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.homePage'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.password =bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.add(user)
        db.session.commit()

        msg_success = f"""
            Hey {form.username.data},
            votre compte a été créé ! Connectez-vous maintenant !
        """
        flash(msg_success, "success")
        return redirect(url_for('auth.loginPage'))

    page_title = "Je m'inscris"

    return render_template(
        'pages/auth/register.html',
        page_title=page_title, form=form
    )


@auth.route("/account/login/", methods=['GET', 'POST'])
@auth.route("/account/connexion/", methods=['GET', 'POST'])
def loginPage():

    """
    Log-in page for registered users.
    GET requests serve Log-in page.
    POST requests validate and redirect user to dashboard.
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.homePage'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboardPage'))

        flash("Combinaison nom d'utilisateur/mot de passe invalide.", "danger")
        return redirect(url_for('auth.loginPage'))

    page_title = "Connexion"

    return render_template(
        'pages/auth/login.html',
        page_title=page_title, form=form
    )


@auth.route('/account/logout/')
@auth.route('/account/deconnexion/')
@login_required
def logoutPage():
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
