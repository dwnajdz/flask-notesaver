from datetime import timedelta
from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
app.config['SECRET_KEY'] = '2b6ed19cf10b162185975d68ce5b2b7c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nts.db'
# this is for password reset replace it with real email credentials and this will allow you to reset forgotten password
#app.config['MAIL_SERVER'] = 'smtp.gmail.com'
#app.config['MAIL_PORT'] = 587
#app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USERNAME'] = 'examplemail@gmail.com'
#app.config['MAIL_PASSWORD'] = 'examplepassword'
app.config['SESSION_COOKIE_NAME'] = 'nts_sessionid'
app.config['REMEMBER_COOKIE_NAME'] = 'nts_remember' 
app.permanent_session_lifetime = timedelta(minutes=60)

app.app_context().push()
db = SQLAlchemy(app)

db.create_all()
db.session.commit()

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'
csrf = CSRFProtect(app)
mail = Mail(app)

from nts import views