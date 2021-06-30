from app.main import main
from app.models import *


@main.route("/download_milkproject", methods=["POST", "GET"])
@flask_login.login_required
def download_milkproject():
    skus = db.session.query(MilkProjectSKU).all()
    data = [
        {
            'Название SKU': sku.name,
            'Процент': sku.made_from_boilings[0].percent,
            'Название форм фактора': sku.group.name,
            'Линия': "Масло",
            'Имя бренда': sku.brand_name,
            'Вес нетто': sku.weight_netto,
            'Выход': sku.made_from_boilings[0].output_kg,
            'Коробки': sku.in_box,
            'Вес форм фактора': 0,
            'Вода': sku.made_from_boilings[0].boiling_technologies[0].water_collecting_time,
            'Смесь': sku.made_from_boilings[0].boiling_technologies[0].mixture_collecting_time,
            'Производство': sku.made_from_boilings[0].boiling_technologies[0].processing_time,
            'Красный': sku.made_from_boilings[0].boiling_technologies[0].red_time,
            'Название варки': sku.made_from_boilings[0].name,
            'Kод': sku.code,
        }
        for sku in skus
    ]
    df = pd.DataFrame(data)
    filename = "milk_project.xlsx"
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


