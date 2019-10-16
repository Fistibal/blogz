from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lc101@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime)

    def __init__(self, title, body, owner, date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if date is None:
            date = datetime.utcnow()
        self.date = date

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'the_blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("logged in")
            return redirect('/newpost')
        else:
            flash("User password incorrect, or user does not exist", "error")

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        username_error = ''
        password_error = ''
        verify_error = ''

        if username.count(" ") >= 1:
            username_error = "Username cannot have spaces."

        if len(username) < 3 or len(username) > 20:
            username_error = 'Username must be between 3 and 20 characters.'

        if len(password) < 3 or len(password) > 20:
            password_error = 'Password must be between 3 and 20 characters.'
            password = ''
            verify = ''

        if password.count(" ") >= 1:
            password_error = "Password cannot have spaces."
            password = ''
            verify = ''

        if verify != password:
            verify_error = "Password don't match."
            password = ''
            verify = '' 

        if existing_user:
            username_error = "User already exist"

        if not username_error and not password_error and not verify_error: 
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash('Welcome', 'success')
            return redirect('/newpost')
        else:
            # flash("Wrong info, Please try again", 'success')
            return render_template('signup.html', username_error=username_error, password_error=password_error, password=password, verify_error=verify_error, verify=verify)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title="Blogz!", users=users)

    
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html', title="New Blog Entry")

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        user = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(blog_title, blog_body, user)

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
            return render_template('newpost.html', title="Blogz!", blogs=blogs,
                blog_title=blog_title, title_error=title_error, 
                blog_body=blog_body, body_error=body_error)

@app.route('/blog', methods=['POST', 'GET'])
def the_blog():

    if 'id' in request.args:
        blog_id = request.args.get('id')
        blogs = Blog.query.filter_by(id=blog_id)
        return render_template('thePost.html', blogs=blogs)
    
    elif 'user' in request.args:
        blogger = request.args.get('user')
        user = User.query.filter_by(username=blogger).first()
        blogs = user.blogs
        return render_template('singleUser.html', blogger=blogger, user=user, blogs=blogs)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Blogz!", blogs=blogs)


if __name__ == '__main__':
    app.run()
