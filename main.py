from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:lc101@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog!", blogs=blogs)

    
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html', title="New Blog Entry")

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog = Blog(blog_title, blog_body)

        title_error = ''
        body_error = ''

        if len(blog_title) == 0:
            title_error = "Please add a title"
        if len(blog_body) == 0:
            body_error = "Please type your blog entry."

        if not title_error and not body_error:
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog.id))
        
        else:
            blogs = Blog.query.all()
            return render_template('newpost.html', title="Build a Blog!", blogs=blogs,
                blog_title=blog_title, title_error=title_error, 
                blog_body=blog_body, body_error=body_error)

@app.route('/blog', methods=['POST', 'GET'])
def the_blog():
    
    if request.args:
        blog_id = request.args.get('id')
        blogs = Blog.query.filter_by(id=blog_id).first()
        return render_template('thePost.html', blogs=blogs)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog!", blogs=blogs)


if __name__ == '__main__':
    app.run()