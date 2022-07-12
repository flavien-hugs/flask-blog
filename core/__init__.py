import logging as lg

from core import models
from core.views import app

user = models.User(
    username="Flavien HUGS",
    email="flavienhugs@pm.me",
    password="password"
)

post = models.Post(
    user_id=1,
    title="Post one",
    content="First post content one !"
)

def init_database():
    models.db.create_all()
    models.db.session.add(user)
    models.db.session.add(post)
    models.db.session.commit()
    lg.warning('Database initialized !')


models.db.init_app(app)


@app.cli.command('init_db')
def init_db():
    init_database()
