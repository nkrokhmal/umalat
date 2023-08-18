from app.imports.runtime import *
from app.main import main
from app.main.butter.update_task_and_batches import update_task_and_batches as update_task_and_batches_butter
from app.main.mascarpone.update_task_and_batches import update_task_and_batches as update_task_and_batches_mascarpone
from app.main.milk_project.update_task_and_batches import (
    update_task_and_batches as update_task_and_batches_milk_project,
)
from app.main.mozzarella.update_task_and_batches import update_task_and_batches as update_task_and_batches_mozzarella
from app.main.ricotta.update_task_and_batches import update_task_and_batches as update_task_and_batches_ricotta
from app.utils.files.utils import delete_from_approved_pickle, move_to_approved, move_to_approved_pickle


@main.route("/approve", methods=["GET", "POST"])
@flask_login.login_required
def approve():
    date = flask.request.args.get("date")
    file_name = flask.request.args.get("file_name")
    department = flask.request.args.get("department")

    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    _ = move_to_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file

    send_file.queue(os.path.join(path, file_name), date, department)

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".download_schedules", page=1))


@main.route("/disprove", methods=["GET", "POST"])
@flask_login.login_required
def disprove():
    date = flask.request.args.get("date")
    file_name = flask.request.args.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    os.remove(
        os.path.join(
            flask.current_app.config["DYNAMIC_DIR"], date, flask.current_app.config["APPROVED_FOLDER"], file_name
        )
    )
    os.remove(
        os.path.join(
            flask.current_app.config["DYNAMIC_DIR"], date, flask.current_app.config["APPROVED_FOLDER"], pickle_file_name
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

    send_file.queue(os.path.join(path, file_name), date, "Моцарелла")

    # update_task_and_batches_mozzarella((date, 'approved', file_name), boiling_plan_df=flask.request.form.get("boiling_plan_df"))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".mozzarella_schedule"))


@main.route("/approve_upload_mozzarella", methods=["GET", "POST"])
@flask_login.login_required
def approve_upload_mozzarella():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    delete_from_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file

    send_file.queue(os.path.join(path, file_name), date, "Моцарелла")

    update_task_and_batches_mozzarella((date, "approved", file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".mozzarella_upload_schedule"))


@main.route("/approve_ricotta", methods=["GET", "POST"])
@flask_login.login_required
def approve_ricotta():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    _ = move_to_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file

    send_file.queue(os.path.join(path, file_name), date, "Рикотта")

    # update_task_and_batches_ricotta((date, 'approved', file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".ricotta_schedule"))


@main.route("/approve_upload_ricotta", methods=["GET", "POST"])
@flask_login.login_required
def approve_upload_ricotta():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    delete_from_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file

    send_file.queue(os.path.join(path, file_name), date, "Рикотта")

    update_task_and_batches_ricotta((date, "approved", file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".ricotta_upload_schedule"))


@main.route("/approve_mascarpone", methods=["GET", "POST"])
@flask_login.login_required
def approve_mascarpone():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    _ = move_to_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file

    send_file.queue(os.path.join(path, file_name), date, "Маскарпоне")

    # update_task_and_batches_mascarpone((date, 'approved', file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".mascarpone_schedule"))


@main.route("/approve_upload_mascarpone", methods=["GET", "POST"])
@flask_login.login_required
def approve_upload_mascarpone():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    delete_from_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file

    send_file.queue(os.path.join(path, file_name), date, "Маскарпоне")

    update_task_and_batches_mascarpone((date, "approved", file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".mascarpone_upload_schedule"))


@main.route("/approve_butter", methods=["GET", "POST"])
@flask_login.login_required
def approve_butter():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    _ = move_to_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file

    send_file.queue(os.path.join(path, file_name), date, "Масло")

    # update_task_and_batches_butter((date, 'approved', file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".butter_schedule"))


@main.route("/approve_upload_butter", methods=["GET", "POST"])
@flask_login.login_required
def approve_upload_butter():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    delete_from_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file

    send_file.queue(os.path.join(path, file_name), date, "Масло")

    update_task_and_batches_butter((date, "approved", file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".butter_upload_schedule"))


@main.route("/approve_milk_project", methods=["GET", "POST"])
@flask_login.login_required
def approve_milk_project():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    _ = move_to_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file

    send_file.queue(os.path.join(path, file_name), date, "Милкпроджект")

    # update_task_and_batches_milk_project((date, 'approved', file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".milk_project_schedule"))


@main.route("/approve_upload_milk_project", methods=["GET", "POST"])
@flask_login.login_required
def approve_upload_milk_project():
    date = flask.request.form.get("date")
    file_name = flask.request.form.get("file_name")
    pickle_file_name = f"{file_name.split('.')[0]}.pickle"

    path = move_to_approved(date=date, file_name=file_name)
    delete_from_approved_pickle(date=date, file_name=pickle_file_name)

    from app.main.workers.send_file import send_file

    send_file.queue(os.path.join(path, file_name), date, "Милкпроджект")

    update_task_and_batches_milk_project((date, "approved", file_name))

    flask.flash("Расписание успешно утверждено", "success")
    return flask.redirect(flask.url_for(".milk_project_upload_schedule"))
