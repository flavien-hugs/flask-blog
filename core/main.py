"""
Logged-in page routes.
"""

from flask import Blueprint, render_template

from flask_wtf.csrf import CSRFError
from flask_login import login_required, current_user

from core.models import Post


# Blueprint Configuration

main = Blueprint("main", __name__)


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


@main.route("/")
@main.route("/home/")
@main.route("/index/")
@main.route("/accueil/")
def homePage():
    return render_template(
        'pages/index.html'
    )


@main.route("/blog/")
@main.route("/posts/")
def blogListPage():
    page_title = "Blog"
    return render_template(
        'pages/blog.html',
        page_title=page_title, posts=posts
    )


@main.route("/contact-me/")
@main.route("/contact/")
def contactPage():
    page_title = "Laissez-moi un message"
    return render_template(
        'pages/contact.html',
        page_title=page_title
    )


@main.route("/about/")
@main.route("/about-us/")
@main.route("/qui-suis-je/")
def aboutPage():
    page_title = "Qui suis-je ?"
    return render_template(
        'pages/about.html',
        page_title=page_title
    )


@main.route('/account/me/', methods=['GET'])
@main.route('/account/dashboard/', methods=['GET'])
@login_required
def dashboardPage():
    page_title = "Mon compte"
    return render_template(
        'pages/auth/dashboard.html',
        current_user=current_user,
        page_title=page_title
    )


@main.errorhandler(404)
def pageNotFound(error):
    page_title = "Page non trouvé"
    return render_template(
        'pages/error.html',
        page_title=page_title,
        error=error
    ), 404


@main.errorhandler(500)
def serverError(error):
    page_title = "Quelques choses à mal tourné"
    return render_template(
        'pages/error.html',
        page_title=page_title,
        error=error
    ), 500


@main.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template(
        'pages/error.html',
        error=e.description
    ), 400
