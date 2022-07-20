"""
Main page routes.
"""

from flask import render_template, url_for, redirect, request, make_response

from flask_login import login_required, current_user

from . import main
from ..blog.forms import CommentForm
from ..decorators import permission_required
from ..models import db, Permission, User, Post, Comment


@main.route("/", strict_slashes=False)
@main.route("/home/", strict_slashes=False)
@main.route("/index/", strict_slashes=False)
@main.route("/accueil/", strict_slashes=False)
def homePage():
    show_followed = False

    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    authors_count = User.query.count()
    posts_count = Post.query.count()
    posts = query.order_by(Post.date_posted.desc()).limit(6)
    return render_template(
        'pages/index.html',
        posts=posts,
        posts_count=posts_count,
        authors_count=authors_count,
        show_followed=show_followed
    )


@main.route("/blog/", strict_slashes=False)
@main.route("/posts/", strict_slashes=False)
def blogListPage():
    page_title = "Blog"

    show_followed = False

    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_follewed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    page = request.args.get('page', 1, type=int)
    posts_list = query.order_by(Post.date_posted.desc())
    pagination = posts_list.paginate(page=page, per_page=8, error_out=False)
    posts = pagination.items

    return render_template(
        'pages/blog.html',
        posts=posts,
        page_title=page_title,
        pagination=pagination,
        show_followed=show_followed
    )


@main.route("/article/<string:post_slug>/", methods=['GET', 'POST'], strict_slashes=False)
def postDetailPage(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            post=post,
            content=form.content.data,
            author=current_user._get_current_object()
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('main.postDetailPage', post_slug=post.slug, page=-1))

    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // 8 + 1

    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=8, error_out=False)
    comments = pagination.items
    return render_template(
        'post/detail.html',
        post=post, form=form,
        comments=comments,
        pagination=pagination,
        page_title=post.title.capitalize()
    )


@main.route('/author/<string:slug>/', methods=['GET'], strict_slashes=False)
def userProfilePage(slug):
    user = User.query.filter_by(slug=slug).first_or_404()
    if user is None:
        abort(404)

    page = request.args.get('page', 1, type=int)
    page_title = user.username.capitalize()
    pagination = user.posts.order_by(Post.date_posted.desc()).paginate(
        page=page, per_page=5, error_out=False)
    posts = pagination.items

    return render_template(
        'pages/user.html',
        user=user,
        posts=posts,
        pagination=pagination,
        page_title=page_title
    )


@main.route('/follow/<string:slug>')
@login_required
@permission_required(Permission.FOLLOW)
def followPage(slug):
    user = User.query.filter_by(slug=slug).first()
    if user is None:
        flash('Utilisation invalide.')
        return redirect(url_for('main.homePage'))

    if current_user.is_following(user):
        flash(f"Vous suivez déjà l'utilisateur: {user.username}")
        return redirect(url_for('main.homePAge'))

    current_user.follow(user)
    db.session.commit()
    flash(f"Vous suivez maintenant {user.username}")
    return redirect(url_for('main.homePAge', slug=user.slug))


@main.route('/followers/<string:slug>')
def followersPage(slug):
    user = User.query.filter_by(slug=slug).first()
    if user is None:
        flash('Utilisation invalide.')
        return redirect(url_for('main.homePage'))

    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=8, error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]

    render_template(
        'pages/followers.html',
        user=user, page_title="Les abonnés",
        endpoint='.followers',
        pagination=pagination,
        follows=follows
    )


@main.route('/all')
@login_required
def showAllPage():
    resp = make_response(redirect(url_for('main.homePage')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def showFollowedPage():
    resp = make_response(redirect(url_for('main.homePage')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


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

    author = User.query.filter_by(
        username=current_user.username).first_or_404()
    posts = author.posts.order_by(Post.date_posted.desc()).limit(6)
    posts_count = author.posts.count()

    return render_template(
        'auth/dashboard.html',
        posts=posts,
        page_title=page_title,
        posts_count=posts_count,
        current_user=current_user
    )
