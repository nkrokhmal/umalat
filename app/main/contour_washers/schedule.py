from app.imports.runtime import *
from app.main import main
from app.main.errors import internal_error
from app.scheduler import run_consolidated, run_contour_cleanings
from app.scheduler.adygea.properties.adygea_properties import AdygeaProperties
from app.scheduler.butter.properties.butter_properties import ButterProperties
from app.scheduler.mascarpone.properties import MascarponeProperties
from app.scheduler.milk_project.properties.milk_project_properties import MilkProjectProperties
from app.scheduler.mozzarella.properties.mozzarella_properties import MozzarellaProperties
from app.scheduler.ricotta.properties import RicottaProperties

from .forms import ScheduleDateForm, ScheduleForm, create_form, fill_properties


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
        milk_project_form = create_form(flask.request.form, MilkProjectProperties())
        adygea_form = create_form(flask.request.form, AdygeaProperties())

        date_str = date
        date = datetime.strptime(date, "%Y-%m-%d")

        if flask.request.method == "GET":
            path = os.path.join(
                flask.current_app.config["DYNAMIC_DIR"],
                date_str,
                flask.current_app.config["APPROVED_FOLDER"],
            )
            schedules = load_schedules(path, date_str)
            props = load_properties(schedules, path=path, prefix=date_str)

            assert_properties_presence(
                props,
                warn_if_not_present=[
                    "mozzarella",
                    "ricotta",
                    "butter",
                    "adygea",
                    "milk_project",
                    "mascarpone",
                ],
            )

            # fill main form
            with code("fill yesterday form values"):
                yesterday = date - timedelta(days=1)
                yesterday_str = yesterday.strftime("%Y-%m-%d")

                yesterday_schedules = load_schedules(
                    config.abs_path("app/data/dynamic/{}/approved/".format(yesterday_str)),
                    prefix=yesterday_str,
                    departments=["ricotta", "mozzarella", "adygea", "milk_project"],
                )
                yesterday_properties = load_properties(
                    yesterday_schedules,
                    path=config.abs_path("app/data/dynamic/{}/approved/".format(yesterday_str)),
                    prefix=yesterday_str,
                )

                if yesterday_properties["mozzarella"].is_present():
                    main_form.molder.data = yesterday_properties["mozzarella"].bar12_present
                else:
                    flask.flash(
                        "Отсутствует утвержденное расписание по моцарелльному цеху за вчера (определяет, нужен ли формовщик)",
                        "warning",
                    )

                if yesterday_properties["ricotta"].is_present():
                    main_form.ricotta_n_boilings_yesterday.data = yesterday_properties["ricotta"].n_boilings
                else:
                    flask.flash(
                        "Отсутствует утвержденное расписание по рикоттному цеху за вчера (определяет число варок для скотты)",
                        "warning",
                    )

                if yesterday_properties["milk_project"].is_present():
                    main_form.ricotta_n_boilings_yesterday.data = yesterday_properties["milk_project"].n_boilings
                else:
                    flask.flash(
                        "Отсутствует утвержденное расписание по милк-проджекты за вчера (определяет число варок для скотты)",
                        "warning",
                    )

                if yesterday_properties["adygea"].is_present():
                    main_form.adygea_n_boilings_yesterday.data = yesterday_properties["adygea"].n_boilings
                else:
                    flask.flash(
                        "Отсутствует утвержденное расписание по адыгейскому цеху за вчера (определяет число варок для скотты)",
                        "warning",
                    )

                main_form.is_tomorrow_not_working_day.data = (
                    date + timedelta(days=1)
                ).weekday() not in config.WORKING_WEEKDAYS

            # fill department forms
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
                    if isinstance(value, list):
                        getattr(form, department + "__" + key).data = json.dumps(value)
                    else:
                        getattr(form, department + "__" + key).data = value

            return flask.render_template(
                "contour_washers/schedule_date.html",
                mozzarella_form=mozzarella_form,
                ricotta_form=ricotta_form,
                mascarpone_form=mascarpone_form,
                butter_form=butter_form,
                milk_project_form=milk_project_form,
                adygea_form=adygea_form,
                main_form=main_form,
                date=date_str,
                params=True,
            )

        if flask.request.method == "POST":
            # fill properties
            form = flask.request.form.to_dict(flat=True)
            properties = {
                "mozzarella": fill_properties(form, MozzarellaProperties()),
                "ricotta": fill_properties(form, RicottaProperties()),
                "mascarpone": fill_properties(form, MascarponeProperties()),
                "butter": fill_properties(form, ButterProperties()),
                "milk_project": fill_properties(form, MilkProjectProperties()),
                "adygea": fill_properties(form, AdygeaProperties()),
            }

            path = config.abs_path("app/data/dynamic/{}/approved/".format(date_str))

            if not os.path.exists(path):
                raise Exception("Не найдены утвержденные расписания для данной даты: {}".format(date))

            with code("Calc input tanks"):
                try:
                    ricotta_n_boilings = int(main_form.ricotta_n_boilings_yesterday.data)
                    adygea_n_boilings = int(main_form.adygea_n_boilings_yesterday.data)
                    milk_project_n_boilings = int(main_form.milk_project_n_boilings_yesterday.data)
                except Exception as e:
                    return internal_error(e)

                input_tanks = calc_scotta_input_tanks(ricotta_n_boilings, adygea_n_boilings, milk_project_n_boilings)
            run_contour_cleanings(
                path,
                properties=properties,
                output_path=path,
                prefix=date_str,
                input_tanks=input_tanks,
                is_tomorrow_day_off=utils.cast_bool(main_form.is_tomorrow_not_working_day.data),
                shipping_line=utils.cast_bool(main_form.shipping_line.data),
                molder=utils.cast_bool(main_form.molder.data),
            )
            run_consolidated(
                path,
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
                milk_project_form=milk_project_form,
                adygea_form=adygea_form,
            )

        return flask.redirect(flask.url_for(".contour_washers_schedule"))
