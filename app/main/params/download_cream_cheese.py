# from app.main import main
# from app.models import Cre
#
#
# @main.route("/download_cream_cheese", methods=["POST", "GET"])
# @flask_login.login_required
# def download_cream_cheese():
#     skus = db.session.query(CreamCheeseSKU).all()
#     data = [
#         {
#             "Название SKU": sku.name,
#             "Процент": sku.made_from_boilings[0].percent,
#             "Название форм фактора": sku.group.name,
#             "Линия": "Маскарпоне",
#             "Имя бренда": sku.brand_name,
#             "Вес нетто": sku.weight_netto,
#             "Коробки": sku.in_box,
#             "Вес форм фактора": sku.form_factor.relative_weight,
#             "Выход": sku.made_from_boilings[0].output_kg,
#             "Срок хранения": sku.shelf_life,
#             "Коэффициент": sku.made_from_boilings[0].output_coeff,
#             "Скорость упаковки": sku.packing_speed,
#             "Охлаждение": sku.made_from_boilings[0].boiling_technologies[0].cooling_time,
#             "Сепарирование": sku.made_from_boilings[0].boiling_technologies[0].separation_time,
#             "Посолка": sku.made_from_boilings[0].boiling_technologies[0].salting_time,
#             "П": sku.made_from_boilings[0].boiling_technologies[0].p_time,
#             "Kод": sku.code,
#         }
#         for sku in skus
#     ]
#     df = pd.DataFrame(data)
#     filename = "cream_cheese.xlsx"
#     excel_path = os.path.join(
#         os.path.dirname(flask.current_app.root_path), flask.current_app.config["UPLOAD_TMP_FOLDER"], filename
#     )
#     df.to_excel(excel_path)
#     response = flask.send_from_directory(
#         directory=os.path.join(
#             os.path.dirname(flask.current_app.root_path),
#             flask.current_app.config["UPLOAD_TMP_FOLDER"],
#         ),
#         filename=filename,
#         cache_timeout=0,
#         as_attachment=True,
#     )
#     response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
#     return response
