# core.models.py

import hashlib
from time import time
from datetime import datetime

from flask import current_app, redirect, flash, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash

import jwt
from slugify import slugify
from . import db, login_manager
from .search import SearchableMixin
from flask_login import UserMixin, AnonymousUserMixin


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwagrs):
        super(Role, self).__init__(**kwagrs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return f"Role(id={self.id!r}, name={self.name!r}, users={self.users!r})"

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderateur': [
                Permission.FOLLOW, Permission.COMMENT, Permission.WRITE,
                Permission.MODERATE
            ],
            'Administrateur': [
                Permission.FOLLOW, Permission.COMMENT, Permission.WRITE,
                Permission.MODERATE, Permission.ADMIN
            ]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class Follow(db.Model):
    """Follow User model"""

    __tablename__ = 'follows'
    follower_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"Follow(id={self.id!r}, follower_id={self.follower_id!r}, followed_id={self.followed_id!r})"


class Comment(db.Model):
    """Comment Post model"""

    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    disabled = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return f"Comment(id={self.id!r}, post={self.post!r}, author={self.author!r})"


class User(db.Model, UserMixin):

    """
    User account model
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(
        db.String(5), default="Mr",
        nullable=False,
    )
    email = db.Column(
        db.String(80), unique=True,
        nullable=False
    )
    username = db.Column(
        db.String(80), nullable=False,
        unique=True
    )
    status = db.Column(
        db.String(100), nullable=True,
    )
    slug = db.Column(
        db.String(100), nullable=False,
        index=True, unique=True
    )
    password = db.Column(
        db.String(200), nullable=False,
        unique=False, primary_key=False
    )
    biography = db.Column(
        db.Text, nullable=False,
        default="about me !"
    )
    website = db.Column(
        db.String(60), index=False,
        unique=False, nullable=True
    )
    image_file = db.Column(
        db.String(20), nullable=True,
        default='default.jpg'
    )
    date_joined = db.Column(
        db.DateTime, nullable=False,
        default=datetime.utcnow()
    )
    member_since = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    role_id = db.Column(
        db.Integer, db.ForeignKey('roles.id'),
        nullable=False
    )
    posts = db.relationship(
        'Post',
        backref='author',
        lazy='dynamic'
    )
    comments = db.relationship(
        'Comment',
        backref='author',
        lazy='dynamic'
    )
    followed = db.relationship(
        'Follow',
        lazy='dynamic',
        overlaps="followed,follower",
        foreign_keys=[Follow.follower_id],
        backref=db.backref('follower', lazy='joined'),
        cascade='all, delete-orphan'
    )
    followers = db.relationship(
        'Follow',
        lazy='dynamic',
        overlaps="followed,follower",
        foreign_keys=[Follow.followed_id],
        backref=db.backref('followed', lazy='joined'),
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwagrs):
        super(User, self).__init__(**kwagrs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrateur').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

        if self.email is not None and self.image_file is None:
            self.image_file = self.gravatar_hash()

        self.follow(self)

    def __repr__(self):
        return f"User(id={self.id!r}, email={self.email!r}, username={self.username!r})"


    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def change_email(self):
        self.image_file = self.gravatar_hash()
        db.session.add(self)
        return True

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

    @property
    def password_hash(self):
        return AttributeError('password is not a readable attribute')

    @password_hash.setter
    def password_hash(self, password):
        self.password = generate_password_hash(password_hash)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(followed_id=user.id).first() is None

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id==Post.author_id)\
            .filter_by(Follow.follower_id==self.id)

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Post(SearchableMixin, db.Model):
    """User Post model"""

    __tablename__ = 'posts'
    __searchable__ = ['title', 'content']

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
        db.ForeignKey('users.id'),
        nullable=False
    )
    slug = db.Column(
        db.String(200),
        nullable=False,
        index=True,
        unique=True
    )
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
    )

    def __repr__(self):
        return f"Post(id={self.id!r}, author={self.author!r}, title={self.title!r})"

    @staticmethod
    def generate_post_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)


db.event.listen(User.username, 'set', User.generate_user_slug, retval=False)
db.event.listen(Post.title, 'set', Post.generate_post_slug, retval=False)


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(int(user_id))
    return None
