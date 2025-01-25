import os
from flask import Flask, request, redirect
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__, template_folder='D:\\Git4253\\flask_authentication\\templates')
app.debug = True

# adding configuration for using a sqlite database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/site.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath('dbconnectcode/instance/site.sqlite3')}"
app.config['SQLALCHEMY_ECHO'] = True

print("Database path:", os.path.abspath('dbconnectcode/instance/site.sqlite3'))
print("Database exists:", os.path.exists('dbconnectcode/instance/site.sqlite3'))
print("Instance folder exists:", os.path.exists('dbconnectcode/instance'))

print("Current Working Directory:", os.getcwd())
print("Templates Folder Path:", os.path.join(os.getcwd(), "templates"))

# Creating an SQLAlchemy instance
db = SQLAlchemy(app)

# Settings for migrations
migrate = Migrate(app, db)

# Models
class Profile(db.Model):
    __tablename__ = 'profile'
    # Id : Field which stores unique id for every row in 
    # database table.
    # first_name: Used to store the first name if the user
    # last_name: Used to store last name of the user
    # Age: Used to store the age of the user
    id          = db.Column(db.Integer, primary_key=True)
    first_name  = db.Column(db.String(20), unique=False, nullable=False)
    last_name   = db.Column(db.String(20), unique=False, nullable=False)
    age         = db.Column(db.Integer, nullable=False)

    # repr method represents how one object of this datatable
    # will look like
    def __repr__(self):
        return f"Name : {self.first_name}, Age: {self.age}"

@app.cli.command("seed")
def seed():
    p1 = Profile(first_name="John", last_name="Doe", age=30)
    p2 = Profile(first_name="Jane", last_name="Smith", age=25)
    db.session.add_all([p1, p2])
    db.session.commit()
    print("Database seeded!")


# function to render index page
@app.route('/')
def index():
    profiles = Profile.query.all()
    return render_template('sqlitedb/index.html', profiles=profiles)

@app.route('/add_data')
def add_data():
    return render_template('sqlitedb/add_profile.html')

# function to add profiles
@app.route('/add', methods=["POST"])
def profile():
    # In this function we will input data from the 
    # form page and store it in our database. Remember 
    # that inside the get the name should exactly be the same 
    # as that in the html input fields
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    age = request.form.get("age")

    # create an object of the Profile class of models and 
    # store data as a row in our datatable
    if first_name != '' and last_name != '' and age is not None:
        p = Profile(first_name=first_name, last_name=last_name, age=age)
        db.session.add(p)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')

@app.route('/delete/<int:id>')
def erase(id):
    
    # deletes the data on the basis of unique id and 
    # directs to home page
    data = Profile.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run()
