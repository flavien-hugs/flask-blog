"""
Routes for user post.
"""

import os
import secrets

from flask import(
    Blueprint, render_template, redirect, request,
    flash, url_for, abort
)

from PIL import Image
from flask_login import login_required, current_user

from core import db
from core.models import Post
from core.forms import PostForm

# Blueprint Configuration
post = Blueprint("post", __name__, url_prefix='/account/dashboard/')


def save_post_picture(picture):
    random_hex = secrets.token_hex(8)
    _, extension = os.path.splitext(picture.filename)
    picture_fn = random_hex + extension
    picture_path = os.path.join(auth.root_path, 'media/post/', picture_fn)

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
    if form.validate_on_submit():

        if not form.title.data:
            flash("Veuillez définir le titre de l'article !")
        if not form.content.data:
            flash("Veuillez définir le contenu de l'article !")
        try:
            post = Post(
                title=form.title.data,
                content=form.content.data,
                post_cover=save_post_picture(form.picture.data),
                author=current_user
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
    author = current_user.id
    posts = Post.query.filter_by(user_id=author)
    page_title = "Liste de vos articles"

    return render_template(
        'auth/posts.html',
        posts=posts, page_title=page_title
    )


@post.route("/post/<int:post_id>/update/", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def postUpdatePage(post_id):
    post = Post.query.get_or_404(post_id)
    page_title = f"Mettre à jour l'article '{post.title}'"
    if post.author != current_user:
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
