"""
Main page routes.
"""


from urllib.parse import urlparse
from datetime import datetime, date, timedelta

from flask import(
    g, render_template, url_for, redirect, flash,
    current_app, request, make_response, Response
)

from flask_login import login_required, current_user

from . import main
from ..email import send_email
from ..blog.forms import CommentForm
from .forms import SearchForm, ContactForm
from ..decorators import permission_required
from ..models import db, Permission, User, Post, Comment, Contact


@main.route("/", strict_slashes=False)
def homePage():
    return render_template('pages/index.html')


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
        user=user,
        follows=follows,
        pagination=pagination,
        page_title="Les abonnés",
    )


@main.before_app_request
def beforeRequest():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@main.context_processor
def mainContextProcessor():
    form = SearchForm()
    return dict(form=form)


@main.route('/search/', strict_slashes=False)
def searchPostPage():
    query = g.search_form.query.data
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(query, page, 8)
    next_url = url_for('main.searchPostPage', query=query, page=page + 1)\
        if total > page * 8 else None
    prev_url = url_for('main.searchPostPage', query=query, page=page - 1)\
        if total > 1 else None

    return render_template(
        'pages/search.html',
        page_title='Recherche',
        posts=posts,
        next_url=next_url,
        prev_url=prev_url
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


@main.route("/contact-us/", methods=['GET', 'POST'], strict_slashes=False)
@main.route("/contact/", methods=['GET', 'POST'], strict_slashes=False)
def contactPage():

    form = ContactForm()
    if form.validate_on_submit():
        try:
            message = Contact(
                fullname=form.fullname.data,
                email=form.email.data.lower(),
                subject=form.subject.data,
                message=form.message.data
            )
            db.session.add(message)
            db.session.commit()
            msg_success = f"""
                Hey {form.fullname.data},
                votre message a été envoyé avec success.
                Nous vous contacterons dans un bref délais.
            """
            flash(msg_success, "success")
            send_email(
                subject=form.subject.data.capitalize(),
                sender=current_app.config['MAIL_SENDER'],
                recipients=['flavienhugs@pm.me'],
                text_body=render_template(
                    'paths/_message.txt', to=form.email.data.lower(),
                    message=form.message.data),
                html_body=render_template(
                    'paths/_message.html', to=form.email.data.lower(),
                    message=form.message.data)
            )
            return redirect(url_for('main.contactPage'))
        except Exception as e:
            return f"Une erreur s'est produite: {e}"

    page_title = "Laissez-nous un message"

    return render_template(
        'pages/contact.html',
        page_title=page_title,
        form=form
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
    comments_count = author.comments.count()

    return render_template(
        'auth/dashboard.html',
        posts=posts,
        page_title=page_title,
        posts_count=posts_count,
        comments_count=comments_count,
        current_user=current_user,
        datetime=date.today() + timedelta(days=3)
    )


@main.route("/sitemap/", strict_slashes=False)
@main.route("/sitemap.xml/", strict_slashes=False)
def sitemap():
    """
        Route to dynamically generate a sitemap of your website/application.
        lastmod and priority tags omitted on static pages.
        lastmod included on dynamic content such as blog posts.
    """

    host_components = urlparse(request.host_url)
    host_base = host_components.scheme + "://" + host_components.netloc

    # Static routes with static content
    static_urls = list()
    for rule in current_app.url_map.iter_rules():
        if(
            not str(rule).startswith("/admin")
            and not str(rule).startswith("/account")
        ):
            if "GET" in rule.methods and len(rule.arguments) == 0:
                url = {
                    "loc": f"{host_base}{str(rule)}",
                    "changefreq": "weekly",
                    "priority": "0.9"
                }
                static_urls.append(url)

    # Dynamic routes with dynamic content
    dynamic_urls = list()
    blog_posts = Post.query.order_by(Post.date_posted.desc()).all()
    for post in blog_posts:
        url = {
            "loc": f"{host_base}/article/{post.slug}",
            "lastmod": post.date_posted.strftime("%Y-%m-%d"),
            "changefreq": "weekly",
            "priority": "0.7"
        }
        dynamic_urls.append(url)

    xml_sitemap = render_template(
        "sitemap.xml", static_urls=static_urls,
        dynamic_urls=dynamic_urls, host_base=host_base
    )
    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"

    return response


@main.route('/robots.txt/', strict_slashes=False)
def noindex():
    Disallow = lambda string: f'Disallow: {string}'
    r = Response(
        "User-Agent: *\n{0}\n".format("\n".join(
            [
                Disallow('/admin/'),
                Disallow('/account/')
            ])),
            status=200, mimetype="text/plain"
        )
    r.headers["Content-Type"] = "text/plain; charset=utf-8"
    return r
