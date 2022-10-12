from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_ckeditor import CKEditor
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
app.config['CKEDITOR_HEIGHT'] = 300
app.config['SECRET_KEY'] = '3c33b8874083c78b15cf465c32973cad'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myblog.db'
db = SQLAlchemy(app)
admin = Admin(app, name='Control Panel')
Login_Manager = LoginManager(app)
Login_Manager.login_view = 'login'
Login_Manager.login_message_category = 'info'
bcrypt = Bcrypt(app)



from app import routes