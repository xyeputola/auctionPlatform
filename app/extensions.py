from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
login_manager = LoginManager() #логин
migrate = Migrate() #изменение бд
csrf = CSRFProtect() #защита