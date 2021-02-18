from flask import render_template
from .. import main


@main.route('/mozzarella_params', methods=['GET'])
def mozzarella_params():
    return render_template('mozzarella_params.html')
