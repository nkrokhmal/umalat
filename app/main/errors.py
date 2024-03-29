from app.imports.runtime import *
from app.main import main


@main.errorhandler(400)
def bad_request(message):
    response = flask.jsonify({"error": "bad request", "message": message})
    response.status_code = 400
    return response


@main.errorhandler(401)
def unauthorized(message):
    response = flask.jsonify({"error": "unauthorized", "message": message})
    response.status_code = 401
    return response


@main.errorhandler(403)
def forbidden(message):
    response = flask.jsonify({"error": "forbidden", "message": message})
    response.status_code = 403
    return response


@main.errorhandler(ValueError)
def validation_error(e):
    return bad_request(e.args[0])


@main.errorhandler(404)
def not_found(e):
    return flask.render_template("404.html"), 404


@main.errorhandler(500)
def internal_error(error):
    original = getattr(error, "original_exception", str(error))
    trace = traceback.format_exc()
    return flask.render_template("500.html", error=original, trace=trace), 500
