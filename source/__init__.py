from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_admin import Admin
from flask_wtf import CsrfProtect
from flask_mail import Mail


app = Flask(__name__,template_folder='templates')
app.config.from_object(Config)
db = SQLAlchemy(app)
#migrate = Migrate(app, db)
login = LoginManager(app)
admin=Admin(app)
mail=Mail(app)
#csrf = CsrfProtect()
#csrf.init_app(app)
# WTF_CSRF_CHECK_DEFAULT = False



num_elements_to_generate = 500

from source import routes


from source.models import adminView,user,score,pointTable

admin.add_view(adminView(user,db.session))
admin.add_view(adminView(score,db.session))
admin.add_view(adminView(pointTable,db.session))
