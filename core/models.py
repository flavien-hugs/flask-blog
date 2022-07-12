# core.models.py

import logging as lg
from datetime import datetime

from core import db, login_manager
from flask_login import UserMixin
from flask import redirect, flash, url_for

class User(db.Model, UserMixin):

    """
    User account model
    """

    __tablename__ = 'user'

    id = db.Column(
        db.Integer,
        primary_key=True
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
    password = db.Column(
        db.String(200),
        nullable=False,
        unique=False,
        primary_key=False
    )
    biography = db.Column(
        db.String(180),
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
        index=False,
        unique=False,
        default=datetime.utcnow()
    )
    posts = db.relationship(
        'Post',
        backref='author',
        lazy=True
    )

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


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
        db.String(255),
        unique=True,
        nullable=False
    )
    content = db.Column(
        db.Text,
        nullable=False
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

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


user = User(username="Flavien HUGS", email="flavienhugs@pm.me", password="password")
post = Post(user_id=1, title="Post one", content="First post content one !")


def init_database():
    db.drop_all()
    db.create_all()
    db.session.add(user)
    db.session.add(post)
    db.session.commit()
    lg.warning('Database initialized !')
