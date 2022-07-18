"""
Logged-in page routes.
"""

from flask import Blueprint, render_template, url_for, request

from flask_wtf.csrf import CSRFError
from flask_login import login_required, current_user

from core.models import User, Post


# Blueprint Configuration

main = Blueprint("main", __name__)


@main.route("/", strict_slashes=False)
@main.route("/home/", strict_slashes=False)
@main.route("/index/", strict_slashes=False)
@main.route("/accueil/", strict_slashes=False)
def homePage():
    authors_count = User.query.count()
    posts_count = Post.query.count()
    posts = Post.query.order_by(Post.date_posted.desc()).limit(6)
    return render_template('pages/index.html', posts=posts, posts_count=posts_count, authors_count=authors_count)


@main.route("/blog/", strict_slashes=False)
@main.route("/posts/", strict_slashes=False)
def blogListPage():
    page_title = "Blog"
    page = request.args.get('page', 1, type=int)
    posts_list = Post.query.order_by(Post.date_posted.desc())
    pagination = posts_list.paginate(page=page, per_page=8, error_out=False)
    posts = pagination.items
    
    return render_template(
        'pages/blog.html', page_title=page_title,
        posts=posts, pagination=pagination
    )


@main.route("/contact-me/", strict_slashes=False)
@main.route("/contact/", strict_slashes=False)
def contactPage():
    page_title = "Laissez-moi un message"
    return render_template(
        'pages/contact.html',
        page_title=page_title
    )


@main.route("/about/", strict_slashes=False)
@main.route("/about-us/", strict_slashes=False)
@main.route("/qui-suis-je/", strict_slashes=False)
def aboutPage():
    page_title = "Qui suis-je ?"
    return render_template(
        'pages/about.html',
        page_title=page_title
    )


@main.route('/account/me/', methods=['GET'], strict_slashes=False)
@main.route('/account/dashboard/', methods=['GET'], strict_slashes=False)
@login_required
def dashboardPage():
    page_title = "Mon compte"
    
    author = User.query.filter_by(username=current_user.username).first_or_404()
    posts = author.posts.order_by(Post.date_posted.desc()).limit(6)
    posts_count = author.posts.count()

    return render_template(
        'auth/dashboard.html',
        posts=posts,
        page_title=page_title,
        posts_count=posts_count,
        current_user=current_user
    )


@main.route("/article/<string:post_slug>/", methods=['GET'], strict_slashes=False)
def postDetailPage(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    return render_template(
        'post/detail.html',
        post=post, page_title=post.title
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
def internalServerError(error):
    page_title = "Quelques choses à mal tourné"
    return render_template(
        'pages/error.html',
        page_title=page_title,
        error=error
    ), 500


@main.errorhandler(CSRFError)
def handleCsrfError(error):
    return render_template(
        'pages/error.html',
        error=error.description
    ), 400
