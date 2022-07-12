# core.routers.py

from flask import(
    render_template, flash, redirect,
    flash, url_for, session
)
from flask_wtf.csrf import CSRFError

from core import app
from core.models import User, Post
from core.forms import RegistrationForm, LoginForm


posts = [
    {
        'author': 'Flavien HUGS',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 22, 2022'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 23, 2022'
    }
]


@app.route("/")
@app.route("/home/")
@app.route("/index/")
@app.route("/accueil/")
def homePage():
    return render_template('pages/index.html')


@app.route("/blog/")
@app.route("/posts/")
def blogListPage():
    page_title = "Blog"
    return render_template('pages/blog.html', page_title=page_title, posts=posts)


@app.route("/contact-me/")
@app.route("/contact/")
def contactPage():
    page_title = "Laissez-moi un message"
    return render_template('pages/contact.html', page_title=page_title)


@app.route("/about/")
@app.route("/about-us/")
@app.route("/qui-suis-je/")
def aboutPage():
    page_title = "Qui suis-je ?"
    return render_template('pages/about.html', page_title=page_title)


@app.route("/register/", methods=['GET', 'POST'])
@app.route("/inscription/", methods=['GET', 'POST'])
def registerPage():
    page_title = "Inscription"
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data } !", "success")
        return redirect(url_for('homePage'))

    return render_template(
        'pages/auth/register.html',
        page_title=page_title, form=form
    )


@app.route("/login/", methods=['GET', 'POST'])
@app.route("/connexion/", methods=['GET', 'POST'])
def loginPage():
    page_title = "Connexion"
    form = LoginForm()
    if(
        form.email.data == 'admin@pm.me'
        and form.password.data == 'password'
    ):
        flash(f"You have been logged in {form.email.data } !", "success")
        return redirect(url_for('homePage'))
    else:
        flash(f"Login unsuccessful. Please check email and password !", "danger")

    return render_template(
        'pages/auth/login.html',
        page_title=page_title, form=form
    )


@app.route('/logout/')
@app.route('/deconnexion/')
def logoutPage():
    session.clear()
    return redirect(url_for('homePage'))


@app.errorhandler(404)
def pageNotFound(error):
    page_title = "Page non trouvé"
    return render_template('pages/error.html', page_title=page_title, error=error), 404


@app.errorhandler(500)
def serverError(error):
    page_title = "Quelques choses à mal tourné"
    return render_template('pages/error.html', page_title=page_title, error=error), 500


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('pages/error.html', error=e.description), 400
