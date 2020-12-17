from flask import send_from_directory
from . import main
from .. utils.generate_constructor import *


@main.route('/download_boiling_plan/<file_name>', methods=['POST', 'GET'])
def download_boiling_plan(file_name):
    uploads = os.path.join(os.path.dirname(current_app.root_path), current_app.config['BOILING_PLAN_FOLDER'])
    return send_from_directory(directory=uploads,
                               filename=file_name,
                               as_attachment=True)


@main.route('/download_sku_plan/<file_name>', methods=['POST', 'GET'])
def download_sku_plan(file_name):
    uploads = os.path.join(os.path.dirname(current_app.root_path), current_app.config['SKU_PLAN_FOLDER'])
    return send_from_directory(directory=uploads,
                               filename=file_name,
                               as_attachment=True)


@main.route('/download_stats/<file_name>', methods=['POST', 'GET'])
def download_stats(file_name):
    uploads = os.path.join(os.path.dirname(current_app.root_path), current_app.config['STATS_FOLDER'])
    return send_from_directory(directory=uploads,
                               filename=file_name,
                               as_attachment=True)


@main.route('/download_schedule/<file_name>', methods=['POST', 'GET'])
def download_schedule(file_name):
    uploads = os.path.join(os.path.dirname(current_app.root_path), current_app.config['SCHEDULE_PLAN_FOLDER'])
    return send_from_directory(directory=uploads,
                               filename=file_name,
                               as_attachment=True)



