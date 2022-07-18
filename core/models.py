# core.models.py

import hashlib
import logging as lg
from time import time
from datetime import datetime

from flask import redirect, flash, url_for, request

import jwt
from slugify import slugify
from flask_login import UserMixin
from core import db, app, login_manager


class User(db.Model, UserMixin):

    """
    User account model
    """

    __tablename__ = 'user'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    gender = db.Column(
        db.String(5),
        default="Mr",
        nullable=False,
    )
    email = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )
    username = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )
    slug = db.Column(
        db.String(100),
        nullable=False,
        index=True,
        unique=True
    )
    password = db.Column(
        db.String(200),
        nullable=False,
        unique=False,
        primary_key=False
    )
    biography = db.Column(
        db.Text,
        nullable=False,
        default="about me !"
    )
    website = db.Column(
        db.String(60),
        index=False,
        unique=False,
        nullable=True
    )
    image_file = db.Column(
        db.String(20),
        nullable=True,
        default='default.jpg'
    )
    date_joined = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )
    posts = db.relationship(
        'Post',
        backref='author',
        lazy='dynamic'
    )

    def __repr__(self):
        return f"User({self.username}', '{self.email}')"

    def generate_reset_token(self):
        return jwt.encode(
            {
                'exp': time() + app.config['RESET_TOKEN_MINUTES'] * 60,
                'reset_email': self.email,
            },
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(token):
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
        except jwt.PyJWTError:
            return
        return User.query.get(email=data['reset_email'])

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=256, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
            hasher = self.image_file or self.gravatar_hash()
        return f"{url}/{hasher}?s={size}&d={default}&r={rating}"

    @staticmethod
    def generate_user_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)



class Post(db.Model):
    """
    User Post model
    """

    __tablename__ = 'post'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    title = db.Column(
        db.String(200),
        unique=True,
        nullable=False
    )
    content = db.Column(
        db.Text
    )
    post_cover = db.Column(
        db.String(20),
        nullable=True,
        default='default.jpg'
    )
    date_posted = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )
    slug = db.Column(
        db.String(200),
        nullable=False,
        index=True,
        unique=True
    )

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

    @staticmethod
    def generate_post_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)


db.event.listen(User.username, 'set', User.generate_user_slug, retval=False)
db.event.listen(Post.title, 'set', Post.generate_post_slug, retval=False)


def init_database():
    db.create_all()
    db.session.commit()
    lg.warning('Database initialized !')
