from app.main import main
from app.models import *


def duplicate(l):
    if isinstance(l, list):
        if len(l) == 1:
            return l * 2
        else:
            return l
    else:
        raise Exception("Wrong format")


@main.route("/download_mascarpone", methods=["POST", "GET"])
@flask_login.login_required
def download_mascarpone():
    skus = db.session.query(MascarponeSKU).all()
    data = [
        {
            'Название SKU': sku.name,
            'Процент': sku.made_from_boilings[0].percent,
            'Наличие лактозы': 'Да' if sku.made_from_boilings[0].is_lactose else 'Нет',
            'Вкусовая добавка':  sku.made_from_boilings[0].flavoring_agent,
            'Название форм фактора': sku.group.name,
            'Линия': "Маскарпоне",
            'Имя бренда': sku.brand_name,
            'Вес нетто': sku.weight_netto,
            'Коробки': sku.in_box,
            'Вес форм фактора': '',
            'Срок хранения': '',
            'Упаковщик': '',
            'Скорость упаковки': sku.packing_speed,
            'Прием': json.dumps(duplicate([x.pouring_time for x in sku.made_from_boilings[0].boiling_technologies])),
            'Нагрев': json.dumps(duplicate([x.heating_time for x in sku.made_from_boilings[0].boiling_technologies])),
            'Молочная кислота': json.dumps(duplicate([x.adding_lactic_acid_time for x in sku.made_from_boilings[0].boiling_technologies])),
            'Сепарирование': json.dumps(duplicate([x.pumping_off_time for x in sku.made_from_boilings[0].boiling_technologies])),
            'Вес': "[500,300]",
            'Выход': json.dumps(duplicate([x.output_ton for x in sku.made_from_boilings[0].boiling_technologies])),
            'Коэффициент': sku.made_from_boilings[0].output_coeff,
            'Внесение ингредиентов': sku.made_from_boilings[0].boiling_technologies[0].ingredient_time,
            'Kод': sku.code,
        }
        for sku in skus
    ]
    df = pd.DataFrame(data)
    filename = "mascarpone.xlsx"
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


