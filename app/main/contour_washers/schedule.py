import flask

from app.imports.runtime import *
from app.main import main
from .forms import (
    ScheduleForm,
    create_mozzarella_form,
    RicottaPropertiesForm,
    MascarponePropertiesForm,
    ButterPropertiesForm,
    MilkProjectPropertiesForm,
    AdygeaPropertiesForm,
)
from app.scheduler import run_consolidated, run_contour_cleanings
from app.main.errors import internal_error
from app.scheduler.mozzarella.properties import *
from app.scheduler.contour_cleanings import *


@main.route("/contour_washers_schedule", methods=["GET", "POST"])
@flask_login.login_required
def contour_washers_schedule():
    form = ScheduleForm(flask.request.form)

    mozzarella_form = create_mozzarella_form(flask.request.form)
    ricotta_form = RicottaPropertiesForm(flask.request.form)
    mascarpone_form = MascarponePropertiesForm(flask.request.form)
    butter_form = ButterPropertiesForm(flask.request.form)
    milk_project_form = MilkProjectPropertiesForm(flask.request.form)
    adygea_form = AdygeaPropertiesForm(flask.request.form)

    if flask.request.method == "POST" and "submit_params" in flask.request.form:
        date = form.date.data
        date_str = date.strftime("%Y-%m-%d")

        path = os.path.join(
            flask.current_app.config["DYNAMIC_DIR"],
            date_str,
            flask.current_app.config["APPROVED_FOLDER"],
        )
        schedules = load_schedules(path, date_str)
        props = load_properties(schedules)

        for department, form in [
            ["mozzarella", mozzarella_form],
            ["ricotta", ricotta_form],
            ["mascarpone", mascarpone_form],
            ["butter", butter_form],
            ["milk_project", milk_project_form],
            ["adygea", adygea_form],
        ]:
            if department not in props:
                continue
            for key, value in props[department].__dict__.items():
                form[key].data = getattr(props[key], key)

        return flask.render_template(
            "contour_washers/schedule.html",
            mozzarella_form=mozzarella_form,
            ricotta_form=ricotta_form,
            mascarpone_form=mascarpone_form,
            butter_form=butter_form,
            milk_project_form=milk_project_form,
            adygea_form=adygea_form,
            form=form,
            date=date_str,
            params=True,
        )

    if flask.request.method == "POST" and "submit_file" in flask.request.form:
        date = form.date.data
        date_str = date.strftime("%Y-%m-%d")

        try:
            adygea_n_boilings = int(form.adygea_n_boilings.data)
            milk_project_n_boilings = int(form.milk_project_n_boilings.data)
        except Exception as e:
            return internal_error(e)

        path = config.abs_path("app/data/dynamic/{}/approved/".format(date_str))

        if not os.path.exists(path):
            raise Exception(
                "Не найдены утвержденные расписания для данной даты: {}".format(date)
            )

        # load input tanks from yesterday
        with code("calc input tanks and present of bar12"):
            yesterday = date - timedelta(days=1)
            yesterday_str = yesterday.strftime("%Y-%m-%d")

            yesterday_schedules = load_schedules(
                config.abs_path("app/data/dynamic/{}/approved/".format(yesterday_str)),
                prefix=yesterday_str,
                departments=["ricotta", "mozzarella"],
            )
            yesterday_properties = load_properties(yesterday_schedules)

            if "ricotta" not in yesterday_schedules:
                # todo soon: warning that ricotta is not found from yesterday
                input_tanks = [["4", 0], ["5", 0], ["8", 0]]
            else:
                input_tanks = calc_scotta_input_tanks(
                    yesterday_schedules,
                    extra_scotta=adygea_n_boilings * 370
                    + milk_project_n_boilings * 2400,
                )

            is_bar12_present = yesterday_properties["mozzarella"].bar12_present

        run_contour_cleanings(
            path,
            output_path=path,
            prefix=date_str,
            input_tanks=input_tanks,
            is_tomorrow_day_off=form.is_not_working_day.data,
            butter_end_time=form.butter_end_time.data,
            milk_project_end_time=form.milk_project_end_time.data,
            adygea_end_time=form.adygea_end_time.data,
            shipping_line=form.shipping_line.data,
            is_bar12_present=is_bar12_present,
        )
        run_consolidated(
            path,
            output_path=path,
            prefix=date_str,
        )
        filename = f"{date_str} Расписание общее.xlsx"
        return flask.render_template(
            "contour_washers/schedule.html",
            form=form,
            filename=filename,
            date=date_str,
            mozzarella_form=mozzarella_form,
            ricotta_form=ricotta_form,
            mascarpone_form=mascarpone_form,
            butter_form=butter_form,
            milk_project_form=milk_project_form,
            adygea_form=adygea_form,
            params=True,
        )
    form.date.data = datetime.today() + timedelta(days=1)
    return flask.render_template(
        "contour_washers/schedule.html", form=form, params=False
    )


#
#
#
#
# @main.route("/contour_washers_schedule", methods=["GET", "POST"])
# @flask_login.login_required
# def contour_washers_schedule():
#     form = ScheduleForm(flask.request.form)
#     if flask.request.method == "POST" and "submit" in flask.request.form:
#         date = form.date.data
#         date_str = date.strftime("%Y-%m-%d")
#         is_not_working_day = form.is_not_working_day.data
#         shipping_line = form.shipping_line.data
#         butter_end_time = form.butter_end_time.data
#         milk_project_end_time = form.milk_project_end_time.data
#         adygea_end_time = form.adygea_end_time.data
#
#         # todo soon: make proper error message
#         try:
#             adygea_n_boilings = int(form.adygea_n_boilings.data)
#             milk_project_n_boilings = int(form.milk_project_n_boilings.data)
#         except Exception as e:
#             return internal_error(e)
#
#         path = config.abs_path("app/data/dynamic/{}/approved/".format(date_str))
#
#         if not os.path.exists(path):
#             raise Exception(
#                 "Не найдены утвержденные расписания для данной даты: {}".format(date)
#             )
#
#         # load input tanks from yesterday
#         with code("calc input tanks and present of bar12"):
#             yesterday = date - timedelta(days=1)
#             yesterday_str = yesterday.strftime("%Y-%m-%d")
#             yesterday_schedules = load_schedules(
#                 config.abs_path("app/data/dynamic/{}/approved/".format(yesterday_str)),
#                 prefix=yesterday_str,
#                 departments=["ricotta", "mozzarella"],
#             )
#             if "ricotta" not in yesterday_schedules:
#                 # todo soon: warning that ricotta is not found from yesterday
#                 input_tanks = [["4", 0], ["5", 0], ["8", 0]]
#             else:
#                 input_tanks = calc_scotta_input_tanks(
#                     yesterday_schedules,
#                     extra_scotta=adygea_n_boilings * 370
#                     + milk_project_n_boilings * 2400,
#                 )
#
#             is_bar12_present = calc_is_bar12_present(yesterday_schedules)
#
#         run_contour_cleanings(
#             path,
#             output_path=path,
#             prefix=date_str,
#             input_tanks=input_tanks,
#             is_tomorrow_day_off=is_not_working_day,
#             butter_end_time=butter_end_time,
#             milk_project_end_time=milk_project_end_time,
#             adygea_end_time=adygea_end_time,
#             shipping_line=shipping_line,
#             is_bar12_present=is_bar12_present,
#         )
#         run_consolidated(
#             path,
#             output_path=path,
#             prefix=date_str,
#         )
#         filename = f"{date_str} Расписание общее.xlsx"
#         return flask.render_template(
#             "contour_washers/schedule.html", form=form, filename=filename, date=date_str
#         )
#
#     form.date.data = datetime.today() + timedelta(days=1)
#     return flask.render_template(
#         "contour_washers/schedule.html", form=form, filename=None
#     )
