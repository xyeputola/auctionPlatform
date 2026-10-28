import os
from pathlib import Path

from flask import Flask, render_template
from flask.cli import with_appcontext
import click
from app.extensions import db, login_manager, migrate, csrf
from flask_login import login_required, current_user

from app.models import User, Auction, Category
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
        return render_template("index.html")

    @app.route("/profile")
    @login_required
    def profile():
        user_auction = Auction.query.filter_by(seller_id=current_user.id).all()
        return render_template("profile.html", user=current_user)

    @app.cli.command("seed-categories")
    def seed_categories():
        categories = ["Компьютеры","Телефоны","Аксессуары"]

        for name in categories:
            existing_category = Category.query.filter_by(name=name).first()
            if not existing_category:
                db.session.add(Category(name=name))

            db.session.commit()
            print("Категория добавлена")


    return app
