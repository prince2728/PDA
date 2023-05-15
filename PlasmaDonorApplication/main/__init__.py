import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_mysqldb import MySQL
from flask_mail import Mail
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_TOKEN')
flask_bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)

# Session Timeout
app.permanent_session_lifetime = timedelta(minutes=30)

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('E-MAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL-PASSWORD')
mail = Mail(app)

# MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mohan@0227'
app.config['MYSQL_DB'] = 'PlasmaDonorApp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOAD_FOLDER'] = 'main/static/uploads/'

mysql = MySQL(app)

# Registering Blueprints
from sprint1.routes import sprint1
from sprint2.routes import sprint2
from sprint3.routes import sprint3
from sprint4.routes import sprint4

app.register_blueprint(sprint1)
app.register_blueprint(sprint2)
app.register_blueprint(sprint3)
app.register_blueprint(sprint4)