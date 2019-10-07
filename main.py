from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:12345@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(255))
    posted = db.Column(db.Boolean)

    def __init__(self, name, body):
        self.name = name
        self.body = body
        self.posted = False


@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    
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
            new_blog = Blog(blog_name, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            new_blog_id = new_blog.id
            blog = Blog.query.get(new_blog_id)
            return render_template('/blog.html', blog = blog)

    return render_template('newpost.html', name = "Add New Blog Post")

def blog_checkoff():
  
    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.posted = True
    db.session.add(blog)
    db.session.commit()
    return redirect('/newpost')

@app.route('/blog', methods = ['GET'])
def blog():
    
    blog_id = int(request.args.get('id'))
    blog = Blog.query.get(blog_id)
    
    return render_template('blog.html', blog = blog)   

@app.route('/', methods=['POST', 'GET'])
def index():
    posted_blogs = Blog.query.all()
    return render_template('index.html', posted_blogs = posted_blogs)

if __name__ == '__main__':
    app.run()