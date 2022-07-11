# core.views.py

from flask import Flask, render_template


app = Flask(__name__)
app.config.from_object('config')


posts = [
    {
        'author': 'Flavien HUGS',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 22, 2022'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 23, 2022'
    }
]


@app.route("/")
@app.route("/home/")
@app.route("/index/")
@app.route("/accueil/")
def homePage():
    return render_template('pages/index.html')


@app.route("/blog/")
@app.route("/posts/")
def blogListPage():
    page_title = "Blog"
    return render_template('pages/blog.html', page_title=page_title, posts=posts)


@app.route("/contact-me/")
@app.route("/contact/")
def contactPage():
    page_title = "Laissez-moi un message"
    return render_template('pages/contact.html', page_title=page_title)


@app.route("/about/")
@app.route("/about-us/")
@app.route("/qui-suis-je/")
def aboutPage():
    page_title = "Qui suis-je ?"
    return render_template('pages/about.html', page_title=page_title)


@app.errorhandler(404)
def pageNotFound(error):
    page_title = "Page non trouvé"
    return render_template('pages/error.html', page_title=page_title, error=error), 404


@app.errorhandler(500)
def serverError(error):
    page_title = "Quelques choses à mal tourné"
    return render_template('pages/error.html', page_title=page_title, error=error), 500
