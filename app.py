from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import User, db
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

app.config['SECRET_KEY']='lol123LOL'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from routes import *



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))






if __name__ == '__main__':
    app.run(debug=True)    