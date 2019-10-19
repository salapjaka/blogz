from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12345@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "blogz"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(255))
    # posted = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        # self.posted = False
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(255))
    blogs = db.relationship('Blog', backref = "owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['index','blog','login','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html')
    
    blog_name_error = ''
    blog_body_error = ''
    
    if request.method == 'POST':
        blog_name = request.form.get('blog')
        if len(blog_name) < 1:
            blog_name_error = ('Please fill in the title')
            
        blog_body = request.form.get('blog-body')
        if len(blog_body) < 1:
            blog_body_error = ('Please fill in the body')
        
        if any([blog_name_error, blog_body_error]):
            return render_template('newpost.html', blog_name_error = blog_name_error, blog_body_error = blog_body_error, blog_name=blog_name, blog_body=blog_body)
        else:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_name, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            new_blog_id = new_blog.id
            blog = Blog.query.get(new_blog_id)
            return redirect("/blog?id=" + str(new_blog.id))

    return render_template('newpost.html', name = "Add New Blog Post")

@app.route('/blog', methods = ['POST', 'GET'])
def blog():
    
    # blog_id = int(request.args.get('id'))
    # blog = Blog.query.get(blog_id)
    
    # return render_template('blog.html', blog=blog)   
    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template("singleUser.html", page_title = user.username + "'s Posts!", 
                                                  user_blogs=user_blogs)

    single_post = request.args.get("id")
    if single_post:
        blog = Blog.query.get(single_post)
        return render_template("viewpost.html", blog=blog)
    else:
        blogs = Blog.query.all()
        return render_template("blog.html", page_title="All Blog Posts!", blogs=blogs)

@app.route('/', methods=['POST', 'GET'])
def index():
    # posted_blogs = Blog.query.all()
    # return render_template('index.html', posted_blogs = posted_blogs)
    users = User.query.all()
    return render_template("index.html", users=users)

@app.route("/signup", methods=['GET','POST'])
def signup():
    
    username_error = ''
    password_error = ''
    verify_error = ''

    if request.method == 'GET':
        return render_template("signup.html")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
#username
        if int(len(username)) > 20 or int(len(username)) < 3:
            username_error = "That's not a valid username(value range 3-20), no spaces"
            username = ''
#password
        if int(len(password)) > 20 or int(len(password)) < 3:
            password_error = "That's not a valid password(value range 3-20), no spaces"
            password = ''
#verify
        if password !=verify:
            verify_error = "The passwords do not match"
            verify = ''

        if username_error!='' or password_error!='' or verify_error!='':
            return render_template("signup.html", username=username, username_error=username_error,password_error=password_error, verify_error=verify_error)
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            username_error = "That username already exists"
            return render_template("signup.html", username_error=username_error)

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    else:
        return render_template('signup.html')

@app.route("/login", methods=['GET','POST'])
def login():

    if request.method == 'GET':
        if 'username' not in session:
            return render_template("login.html", page_title='Login')
        else:
            return redirect('/newpost')

    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

        if user and user.password != password:
            password_error = "The password is incorrect"
            return render_template('login.html', password_error=password_error)

        if not user:
            username_error = "This username does not exist"
            return render_template("login.html", username_error=username_error)

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()