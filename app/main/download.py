#
# from io import BytesIO
# from flask import url_for, render_template, flash, request, make_response, current_app, request, send_from_directory
# from pycel import ExcelCompiler
# from werkzeug.utils import redirect
# from . import main
# import pandas as pd
# from .. import db
# from .forms import StatisticForm
# from ..models import SKU, Boiling
# from sqlalchemy import or_, and_
# from flask_restplus import reqparse
# import openpyxl
# from app.interactive_imports import *
# import re
# import numpy as np
# from .. utils.generate_constructor import *
#
#
# # todo: add plan
# # todo: file naming
# @main.route('/generate_boiling_plan', methods=['POST', 'GET'])
# def generate_boiling_plan():
#     print(current_app.root_path)
#     uploads = os.path.join(current_app.root_path, current_app.config['CONSTRUCTOR_LINK_FOLDER'])
#     print(uploads, file.filename)
#     send_from_directory(directory=uploads, filename=file.filename, as_attachment=True)
#     return render_template('boiling_plan_full.html', form=form, link=link)
#
