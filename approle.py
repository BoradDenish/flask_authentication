# import Flask from flask
from flask import Flask
# and store the instance in 'db'
from flask_sqlalchemy import SQLAlchemy
# import UserMixin, RoleMixin
from flask_security import Security, SQLAlchemySessionUserDatastore, UserMixin, RoleMixin
from flask_migrate import Migrate
# import required libraries from flask_login and flask_security
# from flask_login import LoginManager, login_manager, login_user

# import the required libraries
from flask import render_template, redirect, url_for

app = Flask(__name__)
# path to sqlite database
# this will create the db file in instance

# if database not present already
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///newDB.sqlite3"
# needed for session cookies
app.config['SECRET_KEY'] = 'MY_SECRET'
# hashes the password and then stores in the database
app.config['SECURITY_PASSWORD_SALT'] = "MY_SECRET"
# allows new registrations to application
app.config['SECURITY_REGISTERABLE'] = True
# to send automatic registration email to user
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
# import SQLAlchemy for database operations


db = SQLAlchemy()
db.init_app(app)

# runs the app instance
app.app_context().push()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# create table in database for assigning roles
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))    

# create table in database for storing users
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id          = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email       = db.Column(db.String, unique=True)
    password    = db.Column(db.String(255), nullable=False, server_default='')
    active      = db.Column(db.Boolean())
    # backreferences the user_id from roles_users table
    roles       = db.relationship('Role', secondary=roles_users, backref='roled')

# create table in database for storing roles
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id      = db.Column(db.Integer(), primary_key=True)
    name    = db.Column(db.String(80), unique=True)
    
# creates all database tables
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template("approle.html")

# Run code in debug mode
if __name__ == "__main__":
    app.run(debug=True)
