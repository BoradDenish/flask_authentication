# import Flask from flask
from flask import Flask, request
# and store the instance in 'db'
from flask_sqlalchemy import SQLAlchemy
# import UserMixin, RoleMixin
from flask_security import Security, SQLAlchemySessionUserDatastore, UserMixin, RoleMixin, roles_accepted
from flask_migrate import Migrate
# import required libraries from flask_login and flask_security
from flask_login import LoginManager, login_manager, login_user

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
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)  # Added field
    # backreferences the user_id from roles_users table
    roles = db.relationship('Role', secondary=roles_users, backref='roled')

    # Ensure fs_uniquifier is always set
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.fs_uniquifier:
            import uuid
            self.fs_uniquifier = str(uuid.uuid4())


# create table in database for storing roles
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id      = db.Column(db.Integer(), primary_key=True)
    name    = db.Column(db.String(80), unique=True)

# creates all database tables
def create_tables():
    db.create_all()

# @app.before_request
# def initialize_roles():
#     from create_roles import create_roles
#     create_roles()



user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
security = Security(app, user_datastore)


@app.route('/')
def index():
    return render_template("role/approle.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg=""
    # if the form is submitted
    if request.method == 'POST':
    # check if user already exists
        user = User.query.filter_by(email=request.form['email']).first()
        msg=""
        # if user already exists render the msg
        if user:
            msg="User already exist"
            # render signup.html if user exists
            return render_template('signup.html', msg=msg)
        
        # if user doesn't exist
        
        # store the user to database
        user = User(email=request.form['email'], active=1, password=request.form['password'])
        # store the role
        role = Role.query.filter_by(id=request.form['options']).first()
        user.roles.append(role)
        
        # commit the changes to database
        db.session.add(user)
        db.session.commit()
        
        # login the user to the app
        # this user is current user
        login_user(user)
        # redirect to index page
        return redirect(url_for('index'))
        
    # case other than submitting form, like loading the page itself
    else:
        return render_template("role/rolesignup.html", msg=msg)

# signin page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    msg=""
    if request.method == 'POST':
        # search user in database
        user = User.query.filter_by(email=request.form['email']).first()
        # if exist check password
        if user:
            if  user.password == request.form['password']:
                # if password matches, login the user
                login_user(user)
                return redirect(url_for('index'))
            # if password doesn't match
            else:
                msg="Wrong password"
        
        # if user does not exist
        else:
            msg="User doesn't exist"
        return render_template('role/rolesignin.html', msg=msg)
        
    else:
        return render_template("role/rolesignin.html", msg=msg)


@app.route('/teachers')
# only Admin can access the page
@roles_accepted('Admin')
def teachers():
    teachers = []
    # query for role Teacher that is role_id=2
    role_teachers = db.session.query(roles_users).filter_by(role_id=2)
    # query for the users' details using user_id
    for teacher in role_teachers:
        user = User.query.filter_by(id=teacher.user_id).first()
        teachers.append(user)
    # return the teachers list
    return render_template("role/roleteachers.html", teachers=teachers)

# for staff page
@app.route('/staff')
# only Admin and Teacher can access the page
@roles_accepted('Admin', 'Teacher')
def staff():
    staff = []
    role_staff = db.session.query(roles_users).filter_by(role_id=3)
    for staf in role_staff:
        user = User.query.filter_by(id=staf.user_id).first()
        staff.append(user)
    return render_template("role/rolestaff.html", staff=staff)
    
# for student page
@app.route('/students')
# only Admin, Teacher and Staff can access the page
@roles_accepted('Admin', 'Teacher', 'Staff')
def students():
    students = []
    role_students = db.session.query(roles_users).filter_by(role_id=4)
    for student in role_students:
        user = User.query.filter_by(id=student.user_id).first()
        students.append(user)
    return render_template("role/rolestudents.html", students=students)
    
# for details page
@app.route('/mydetails')
# Admin, Teacher, Staff and Student can access the page
@roles_accepted('Admin', 'Teacher', 'Staff', 'Student')
def mydetails():
    return render_template("role/rolemydetails.html")

# Run code in debug mode
if __name__ == "__main__":
    app.run(debug=True)



