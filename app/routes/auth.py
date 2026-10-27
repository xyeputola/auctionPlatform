import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

from app.extensions import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email_format(form, field):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", field.data):
        raise ValidationError("Введите корректный адрес электронной почты.")

class registerForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired(message="Введите имя пользователя:"), Length(min=2, max=20, message="От 2 до 20 символов")])

    email = StringField("Электронная почта", validators=[DataRequired(message="Введите электронную почту:"), validate_email_format])

    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Введите пароль."), Length(min=8, max=128, message="Пароль должен содержать от 8 до 128 символов.")])

    confirm_password = PasswordField(
        "Повторите пароль", validators=[DataRequired(message="Повторите пароль."), EqualTo("password", message="Пароли не совпадают.")])

    submit = SubmitField("Зарегистрироваться:")

class loginForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired(message="Введите имя пользователя:")])
    password = PasswordField("Пароль", validators=[DataRequired(message="Введите пароль.")])

    submit = SubmitField("Войти")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = registerForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Имя пользователя занято", "error")
            return render_template("auth/register.html", form=form)

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Эта электронная почта уже используется.", "error")
            return render_template("auth/register.html", form=form)

        user = User(username=username, email=email, role="user")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Регистрация прошла успешно, войдите в аккаунт", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = loginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(form.password.data):
            login_user(user)

            flash("Успешный вход", "success")
            next_page = request.args.get("next")

            if next_page and next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)

            return redirect(url_for("index"))

        flash("Неверное имя или пароль", "error")

    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "success")
    return redirect(url_for("index"))