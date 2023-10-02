from app.imports.runtime import *
from app.main import main
from app.models import User

from .forms import LoginForm


@main.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm(flask.request.form)
    if "login" in flask.request.form:
        username = flask.request.form["username"]
        password = flask.request.form["password"]

        user = db.session.query(User).filter_by(username=username).first()
        if user and User.verify_pass(password, user.password):
            flask_login.login_user(user)
            return flask.redirect(flask.url_for(".index"))

        return flask.render_template("login.html", msg="Неправильный логин или пароль!", form=login_form)

    if not flask_login.current_user.is_authenticated:
        return flask.render_template("login.html", form=login_form)

    return flask.redirect(flask.url_for(".index"))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.render_template("403.html"), 403
