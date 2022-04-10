from sanic.response import json, HTTPResponse


def json_response(msg: str, status: int = 200, errors: dict = None, **kwargs) -> HTTPResponse:
    response = {'msg': msg, 'errors': errors, **kwargs} if errors else {'msg': msg, **kwargs}
    return json(response, status)
