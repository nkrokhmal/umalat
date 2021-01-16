from flask import jsonify, render_template
from flask_restplus import ValidationError
from . import main


def ok(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 200
    return response


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


@main.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


@main.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@main.errorhandler(500)
def internal_error(error):
    return render_template('500.html', error=error), 500