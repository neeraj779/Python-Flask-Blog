from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json

with open("config.json", "r") as parameters:
    data = json.load(parameters)["params"]

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=data["gmail_id"],
    MAIL_PASSWORD=data["gmail_password"]
)
mail = Mail(app)
if data["local_server"]:
    app.config['SQLALCHEMY_DATABASE_URI'] = data["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = data["production_uri"]
db = SQLAlchemy(app)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(15), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(220), nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    img = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    tag_line = db.Column(db.String(20), nullable=True)
    


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    return render_template("index.html", data=data, posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", data=data)
    
@app.route("/post/<string:post_slug>", methods=["GET"])
def post_route(post_slug):
    post= Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", data=data, post=post)




@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contact(name=name, date=datetime.now(),
                        phone_num=phone, msg=message, email=email) 
        db.session.add(entry)
        db.session.commit()
        mail.send_message(f'New message from {name}',
                          sender=email,
                          recipients=[data["gmail_id"]],
                          body= message + "/n" + phone

                          )

    return render_template("contact.html", data=data)


app.run(debug=True)
