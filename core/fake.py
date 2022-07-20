from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker

from . import db
from .models import User, Post


def users(count=15):
    fake = Faker()
    i = 0
    while i < count:
        user = User(
            email=fake.email(),
            username=fake.name(),
            biography=fake.text(),
            website=fake.hostname(),
            member_since=fake.past_date(),
            last_seen=fake.past_date(),
            password='password',
        )
        db.session.add(user)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=15):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        user = User.query.offset(randint(0, user_count - 1)).first()
        post = Post(
            title=fake.word(),
            content=fake.text(),
            post_cover=fake.image_url(),
            date_posted=fake.past_date(),
            slug=fake.slug(),
            author=user
        )
        db.session.add(post)
    db.session.commit()
