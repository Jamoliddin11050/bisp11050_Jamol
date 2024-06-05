from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
app = Flask(__name__)

# Set the secret key for sessions
app.secret_key = 'i2(x9psz^i14&kym$05mha8t!*gr+neeka%t!i$gso$0#0pjht'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:jamol@localhost/jamol'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Specify the login route

# Importing routes and models
from app import routes, models

@login_manager.user_loader
def load_user(user_id):
    # Return the user object based on the user_id
    return models.User.query.get(int(user_id))

