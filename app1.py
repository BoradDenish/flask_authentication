from flask import *
from flask_sqlalchemy import SQLAlchemy
import re
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash


# Initialize Flask app
app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'hello'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    email       = db.Column(db.String(150), unique=True, nullable=False)
    password    = db.Column(db.String(150), nullable=False)


# Create the database
with app.app_context():
    db.create_all()


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email    = request.form['email']
        password = request.form['password']
        
        # SQLAlchemy query to check user
        user = User.query.filter_by(email=email).first()
        is_valid = bcrypt.check_password_hash(user.password, password)
        if is_valid:        
        # if user and check_password_hash(user.password, password):        
            session['loggedin'] = True
            session['userid']   = user.id
            session['name']     = user.name
            session['email']    = user.email
            message = 'Logged in successfully!'
            return render_template('user.html', message=message)
        else:
            message = 'Please enter correct email/password!'
    
    return render_template('sign_in1.html', message=message)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email    = request.form['email']
        
        # Check if account exists
        account = User.query.filter_by(email=email).first()
        
        if account:
            message = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not userName or not password or not email:
            message = 'Please fill out the form!'
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') 

            # Create a new user
            new_user = User(name=userName, email=email, password=hashed_password)
            # new_user = User(name=userName, email=email, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            message = 'You have successfully registered!'
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    
    return render_template('sign_up1.html', message=message)


# Run code in debug mode
if __name__ == "__main__":
    app.run(debug=True)
