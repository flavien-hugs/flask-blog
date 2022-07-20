"""
"""

from flask import render_template

from flask_wtf.csrf import CSRFError

from . import main


@main.errorhandler(404)
def pageNotFound(error):
    page_title = "Page non trouvé"
    return render_template(
        'pages/error.html',
        page_title=page_title,
        error=error
    ), 404


@main.errorhandler(500)
def internalServerError(error):
    page_title = "Quelques choses à mal tourné"
    return render_template(
        'pages/error.html',
        page_title=page_title,
        error=error
    ), 500


@main.errorhandler(CSRFError)
def handleCsrfError(error):
    return render_template(
        'pages/error.html',
        error=error.description
    ), 400
