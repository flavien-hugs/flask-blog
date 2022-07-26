"""
Application entry point.
"""

import os
import logging as lg

from core import create_app, db
from core.models import Role, User, Post, Comment


app = create_app(os.getenv('FLASK_CONFIG') or 'dev')

@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db, Role=Role,
        User=User, Post=Post, Comment=Comment
    )

@app.cli.command('test')
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command('init_db')
def init_db():
    db.create_all()
    db.session.commit()
    lg.warning('Database initialized !')


if __name__ == "__main__":
    print(app.config['DEBUG'])
    app.run(debug=app.config['DEBUG'])
