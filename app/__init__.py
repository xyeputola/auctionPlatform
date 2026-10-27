import os
from pathlib import Path

from flask import Flask
from app.extensions import db, login_manager, migrate, csrf

from app.models import User
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)
    project_dir = Path(__file__).resolve().parent.parent
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY","dev-key-change-before-deployment")
    app.config["SQLALCHEMY_DATABASE_URI"] = (f"sqlite:///{project_dir / 'auction.db'}")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.route("/")
    def index():
        return """
        <h1>Welcome to Auction Auction Automation!</h1>
        <p>flask work</p>
    """

    return app