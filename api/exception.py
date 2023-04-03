from flask import jsonify
from werkzeug.exceptions import HTTPException

from api import raspiot_api


@raspiot_api.app_errorhandler(HTTPException)
def resource_not_found(e):
    if isinstance(e, HTTPException):
        return jsonify(code=e.code, message=e.description)

    return jsonify(code=500, message=str(e))
