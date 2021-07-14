import flask
from app.imports.runtime import *
from app.utils.files.utils import move_to_approved, move_to_approved_pickle
from app.main import main


@main.route("/approve", methods=["GET", "POST"])
@flask_login.login_required
def approve():
    date = flask.request.args.get("date")
    file_name = flask.request.args.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    _ = move_to_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file
    send_file.queue(os.path.join(path, file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".download_schedules", page=1))


@main.route("/disprove", methods=["GET", "POST"])
@flask_login.login_required
def disprove():
    date = flask.request.args.get("date")
    file_name = flask.request.args.get("file_name")

    os.remove(
        os.path.join(
            flask.current_app.config["DYNAMIC_DIR"],
            date,
            "approved",
            file_name
        )
    )
    flask.flash("Расписание успешно удалено из утвержденных", "success")
    return flask.redirect(flask.url_for(".download_schedules", page=1))


@main.route("/approve_mozzarella", methods=["GET", "POST"])
@flask_login.login_required
def approve_mozzarella():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    _ = move_to_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file
    send_file.queue(os.path.join(path, file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".mozzarella_schedule"))


@main.route("/approve_ricotta", methods=["GET", "POST"])
@flask_login.login_required
def approve_ricotta():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    _ = move_to_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file
    send_file.queue(os.path.join(path, file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".ricotta_schedule"))


@main.route("/approve_mascarpone", methods=["GET", "POST"])
@flask_login.login_required
def approve_mascarpone():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    _ = move_to_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file
    send_file.queue(os.path.join(path, file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".mascarpone_schedule"))


@main.route("/approve_butter", methods=["GET", "POST"])
@flask_login.login_required
def approve_butter():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    _ = move_to_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file
    send_file.queue(os.path.join(path, file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".butter_schedule"))


@main.route("/approve_milkproject", methods=["GET", "POST"])
@flask_login.login_required
def approve_milkproject():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    _ = move_to_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file
    send_file.queue(os.path.join(path, file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".milkproject_schedule"))

