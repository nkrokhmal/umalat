from utils_ak.builtin import cast_bool

from app.imports.runtime import *
from app.main import main
from app.main.contour_washers.forms import ScheduleDateForm, ScheduleForm, create_form, fill_properties
from app.scheduler.adygea.properties.adygea_properties import AdygeaProperties
from app.scheduler.butter.properties.butter_properties import ButterProperties
from app.scheduler.common.run_consolidated import run_consolidated
from app.scheduler.contour_cleanings.draw_frontend.draw_frontend import draw_frontend
from app.scheduler.contour_cleanings.load_properties_by_department import (
    assert_properties_presence,
    load_properties_by_department,
)
from app.scheduler.mascarpone.properties.mascarpone_properties import MascarponeProperties
from app.scheduler.mozzarella.properties.mozzarella_properties import MozzarellaProperties
from app.scheduler.ricotta.properties.ricotta_properties import RicottaProperties


@main.route("/contour_washers_schedule", methods=["GET", "POST"])
@flask_login.login_required
def contour_washers_schedule():
    date = flask.request.args.get("date")
    if date is None:
        form = ScheduleForm()
        form.date.data = datetime.today() + timedelta(days=1)
        return flask.render_template("contour_washers/schedule.html", form=form, params=False)
    else:
        main_form = ScheduleDateForm()
        mozzarella_form = create_form(flask.request.form, MozzarellaProperties())
        ricotta_form = create_form(flask.request.form, RicottaProperties())
        mascarpone_form = create_form(flask.request.form, MascarponeProperties())
        butter_form = create_form(flask.request.form, ButterProperties())
        adygea_form = create_form(flask.request.form, AdygeaProperties())

        date_str = date
        date = datetime.strptime(date, "%Y-%m-%d")

        if flask.request.method == "GET":
            # - Get path

            path = os.path.join(
                flask.current_app.config["DYNAMIC_DIR"],
                date_str,
                flask.current_app.config["APPROVED_FOLDER"],
            )

            # - Load props

            props = load_properties_by_department(path=path, prefix=date_str)

            # - Set is_today_day_off

            main_form.is_today_day_off.data = all(not p.is_present for p in props.values())

            # - Validate props

            assert_properties_presence(
                props,
                warn_if_not_present=[
                    "mozzarella",
                    "butter",
                    "adygea",
                    "ricotta",
                    "mascarpone",
                ],
            )

            # - Fill department forms

            for department, form in [
                ["mozzarella", mozzarella_form],
                ["mascarpone", mascarpone_form],
                ["butter", butter_form],
                ["ricotta", ricotta_form],
                ["adygea", adygea_form],
            ]:
                if department not in props:
                    continue

                for key, value in props[department].__dict__.items():
                    if isinstance(value, list):
                        getattr(form, department + "__" + key).data = json.dumps(value)
                    else:
                        getattr(form, department + "__" + key).data = value

            # - Render template

            return flask.render_template(
                "contour_washers/schedule_date.html",
                mozzarella_form=mozzarella_form,
                ricotta_form=ricotta_form,
                mascarpone_form=mascarpone_form,
                butter_form=butter_form,
                adygea_form=adygea_form,
                main_form=main_form,
                date=date_str,
                params=True,
            )

        if flask.request.method == "POST":
            # fill properties
            form = flask.request.form.to_dict(flat=True)
            properties_by_department = {
                "mozzarella": fill_properties(form, MozzarellaProperties()),
                "butter": fill_properties(form, ButterProperties()),
                "adygea": fill_properties(form, AdygeaProperties()),
                "mascarpone": fill_properties(form, MascarponeProperties()),
                "ricotta": fill_properties(form, RicottaProperties()),
            }

            path = config.abs_path("app/data/dynamic/{}/approved/".format(date_str))

            if not os.path.exists(path):
                raise Exception("Не найдены утвержденные расписания для данной даты: {}".format(date))

            draw_frontend(
                input_path=path,
                properties=properties_by_department,
                output_path=path,
                prefix=date_str,
                naslavuchich=cast_bool(main_form.naslavuchich.data),
                basement_brine=cast_bool(main_form.basement_brine.data),
                is_today_day_off=cast_bool(main_form.is_today_day_off.data),
            )
            run_consolidated(
                input_path=path,
                output_path=path,
                prefix=date_str,
            )
            filename = f"{date_str} Расписание общее.xlsx"
            return flask.render_template(
                "contour_washers/schedule_date.html",
                main_form=main_form,
                filename=filename,
                date=date_str,
                mozzarella_form=mozzarella_form,
                ricotta_form=ricotta_form,
                mascarpone_form=mascarpone_form,
                butter_form=butter_form,
                adygea_form=adygea_form,
            )

        return flask.redirect(flask.url_for(".contour_washers_schedule"))
