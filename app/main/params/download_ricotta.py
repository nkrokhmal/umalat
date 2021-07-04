from app.main import main
from app.models import *


@main.route("/download_ricotta", methods=["POST", "GET"])
@flask_login.login_required
def download_ricotta():
    skus = db.session.query(RicottaSKU).all()
    data = [
        {
            'Название SKU': sku.name,
            'Процент': sku.made_from_boilings[0].percent,
            'Вкусовая добавка':  sku.made_from_boilings[0].flavoring_agent,
            'Название форм фактора': 'Рикотта',
            'Линия': 'Рикотта',
            'Имя бренда': sku.brand_name,
            'Вес нетто': sku.weight_netto,
            'Коробки': sku.in_box,
            'Вес форм фактора': 0,
            'Выход': int(sku.output_per_tank * sku.made_from_boilings[0].number_of_tanks),
            'Количество баков': sku.made_from_boilings[0].number_of_tanks,
            'Скорость упаковки': int(60 * int(sku.output_per_tank * sku.made_from_boilings[0].number_of_tanks) / sku.packing_speed),
            'Подготовка полуфабриката': sku.made_from_boilings[0].analysis[0].preparation_time,
            'Анализ': sku.made_from_boilings[0].analysis[0].analysis_time,
            'Перекачка': sku.made_from_boilings[0].analysis[0].pumping_time,
            'Нагрев': sku.made_from_boilings[0].boiling_technologies[0].heating_time,
            'Выдержка': sku.made_from_boilings[0].boiling_technologies[0].delay_time,
            'Сбор белка': sku.made_from_boilings[0].boiling_technologies[0].protein_harvest_time,
            'Заборс': sku.made_from_boilings[0].boiling_technologies[0].abandon_time,
            'Слив': sku.made_from_boilings[0].boiling_technologies[0].pumping_out_time,
            'Kод': sku.code,

        }
        for sku in skus
    ]
    df = pd.DataFrame(data)
    filename = "ricotta.xlsx"
    excel_path = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["UPLOAD_TMP_FOLDER"],
        filename
    )
    df.to_excel(excel_path)
    response = flask.send_from_directory(
        directory=os.path.join(
            os.path.dirname(flask.current_app.root_path),
            flask.current_app.config["UPLOAD_TMP_FOLDER"],
        ),
        filename=filename,
        cache_timeout=0,
        as_attachment=True,
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


