import datetime
import bleach
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


def sanitize(content):
    """Returns 'clean' HTML content from CKEditor
    content: text
    return: text
    """
    allowed_tags = [
        'a', 'abbr', 'acronym', 'address', 'b', 'br', 'div', 'dl', 'dt',
        'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
        'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'strike',
        'span', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
        'thead', 'tr', 'tt', 'u', 'ul'
    ]

    allowed_attrs = {
        'a': ['href', 'target', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
    }

    cleaned = bleach.clean(content,
                           tags=allowed_tags,
                           attributes=allowed_attrs,
                           strip=True)
    return cleaned


@app.route('/edit-post/<int:index>', methods=['GET', 'POST'])
def edit_post(index):
    requested_post = BlogPost.query.get(index)
    form = CreatePostForm(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        img_url=requested_post.img_url,
        author=requested_post.author,
        body=requested_post.body,
    )

    if form.validate_on_submit():
        requested_post.title = form.title.data
        requested_post.subtitle = form.subtitle.data
        requested_post.img_url = form.img_url.data
        requested_post.author = form.author.data
        requested_post.body = form.body.data
        db.session.commit()
        return redirect(url_for("show_detail", index=requested_post.id))

    return render_template('make-post.html', form=form, amend=True)


@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        title = form.title.data
        subtitle = form.subtitle.data
        submit_date = datetime.datetime.now().strftime('%B %d, %Y')
        author = form.author.data
        img_url = form.img_url.data

        body_content = sanitize(form.body.data)

        blog_post = BlogPost(title=title,
                             subtitle=subtitle,
                             date=submit_date,
                             body=body_content,
                             author=author,
                             img_url=img_url)

        db.session.add(blog_post)
        db.session.commit()
        return redirect('/')
    return render_template("make-post.html", form=form)


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", data=posts)


@app.route("/post/<int:index>")
def show_detail(index):
    requested_post = BlogPost.query.get(index)
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
