"""
Auth app page routes.
"""

from flask import Blueprint

post = Blueprint("post", __name__)

from . import views
from ..models import Permission


@post.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
