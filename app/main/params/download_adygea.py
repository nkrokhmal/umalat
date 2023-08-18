from app.main import main
from app.models import *


@main.route("/download_adygea", methods=["POST", "GET"])
@flask_login.login_required
def download_adygea():
    skus = db.session.query(AdygeaSKU).all()
    data = [
        {
            "Название SKU": sku.name,
            "Процент": sku.made_from_boilings[0].percent,
            "Название форм фактора": sku.group.name,
            "Вход": sku.made_from_boilings[0].input_kg,
            "Выход": sku.made_from_boilings[0].output_kg,
            "Линия": "Адегейский",
            "Имя бренда": sku.brand_name,
            "Вес нетто": sku.weight_netto,
            "Коробки": sku.in_box,
            "Вес форм фактора": 0,
            "Набор": sku.made_from_boilings[0].boiling_technologies[0].collecting_time,
            "Коагуляция": sku.made_from_boilings[0].boiling_technologies[0].coagulation_time,
            "Слив": sku.made_from_boilings[0].boiling_technologies[0].pouring_off_time,
            "Kод": sku.code,
        }
        for sku in skus
    ]
    df = pd.DataFrame(data)
    filename = "adygea.xlsx"
    excel_path = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["UPLOAD_TMP_FOLDER"],
        filename,
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
