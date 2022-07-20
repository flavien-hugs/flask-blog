"""
Routes for user post.
"""

import os
import secrets

from flask import(
    render_template, redirect, request,
    flash, url_for, abort
)

from PIL import Image
from flask_login import login_required, current_user

from .. import db
from . import post
from .forms import PostForm
from ..models import Post, User, Permission


def save_post_picture(picture):
    random_hex = secrets.token_hex(8)
    _, extension = os.path.splitext(picture.filename)
    picture_fn = random_hex + extension
    picture_path = os.path.join(
        post.root_path, '../static/media/post/', picture_fn)

    output_size = (923, 498)
    thumb = Image.open(picture)
    thumb.thumbnail(output_size)
    thumb.save(picture_path)

    return picture_fn


@post.route("/create/post/", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def createPostPage():
    page_title = "Créer un article"

    form = PostForm()
    if (
        current_user.can(Permission.WRITE)
        and form.validate_on_submit()
    ):

        if not form.title.data:
            flash("Veuillez définir le titre de l'article !")
        if not form.content.data:
            flash("Veuillez définir le contenu de l'article !")
        try:
            post = Post(
                title=form.title.data,
                content=form.content.data,
                post_cover=save_post_picture(form.picture.data),
                author=current_user._get_current_object()
            )

            db.session.add(post)
            db.session.commit()

            flash("Votre article a été créé !", 'success')
            return redirect(url_for('post.postListPage'))
        except Exception as e:
            return f"Une erreur s'est produite: {e}"

    return render_template(
        'post/create.html',
        form=form,
        page_title=page_title
    )


@post.route("/posts/", methods=['GET'], strict_slashes=False)
@login_required
def postListPage():
    page_title = "Liste de vos articles"
    page = request.args.get('page', 1, type=int)
    author = User.query.filter_by(
        username=current_user.username).first_or_404()
    pagination = author.posts.order_by(Post.date_posted.desc()).paginate(
        page=page, per_page=5, error_out=False)
    posts = pagination.items

    return render_template(
        'auth/posts.html',
        posts=posts,
        pagination=pagination,
        page_title=page_title
    )


@post.route("/post/<int:post_id>/update/", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def postUpdatePage(post_id):
    post = Post.query.get_or_404(post_id)
    page_title = f"Mettre à jour l'article '{post.title}'"
    if (
        current_user != post.author
        and not current_user.can(Permission.ADMIN)
    ):
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        try:
            if form.picture.data:
                picture_file = save_post_picture(form.picture.data)
                post.post_cover = picture_file

            post.title = form.title.data
            post.content = form.content.data

            db.session.commit()

            flash("Votre article a été mise à jour !", 'success')
            return redirect(url_for('post.postUpdatePage', post_id=post.id))
        except Exception as e:
            return f"Une erreur s'est produite: {e}"
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.picture.data = post.post_cover

    return render_template(
        'post/create.html',
        form=form, post=post,
        page_title=page_title
    )


@post.route("/post/<int:post_id>/delete/", methods=['POST'], strict_slashes=False)
@login_required
def postDeletePage(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    try:
        db.session.delete(post)
        db.session.commit()
        flash(
            f"l'article '{post.title.capitalize()}' a été supprimer !", 'success')
        return redirect(url_for('post.postListPage'))
    except Exception as e:
        return f"Une erreur s'est produite: {e}"
