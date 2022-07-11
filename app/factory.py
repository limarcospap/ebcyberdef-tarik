from .logs.routes import logs_api
from .users.routes import users_api
from .config import Config
from .response import json_response
from .exceptions import ServerException, Unauthorized
from sanic import Sanic
from pathlib import Path
from sanic.request import Request
from sanic.response import HTTPResponse, html, raw


def enable_cors(app: Sanic):

    headers = {'Access-Control-Allow-Headers': '*',
               'Access-Control-Allow-Methods': 'DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT',
               'Access-Control-Allow-Origin': '*',
               'Access-Control-Max-Age': 3600}

    @app.middleware('request')
    async def before_request(request: Request):
        if request.method == 'OPTIONS':
            return raw(body=b'', headers=headers)

    @app.middleware('response')
    async def after_response(request: Request, response: HTTPResponse):
        if request.headers.get('origin'):
            for key, value in headers.items():
                response.headers[key] = value


def create_app(loaded_config: dict) -> Sanic:
    index = None
    config = Config(loaded_config)
    sanic_configs = config.sanic.pop('configs', {})
    build_path = Path(__file__).parents[1] / 'build'

    app = Sanic('eb-cyber-def')
    for key, value in sanic_configs.items():
        setattr(app.config, key.upper(), value)
    app.blueprint(logs_api)
    app.blueprint(users_api)
    app.static('/static', str(build_path / 'static'))

    def load_index(required_path: str) -> HTTPResponse:
        nonlocal index
        if index is None:
            with open(required_path) as f:
                index = html(f.read())
        return index

    @app.middleware('request')
    async def before_request(request: Request) -> HTTPResponse:
        if not request.path.startswith(('/api', '/static', '/favicon.ico')):
            required_path = str(build_path / 'index.html')
            return load_index(required_path)
        # if request.path.startswith('/api/logs'):
        #     user = await Config.current.users.collection.find_one({'_id': request.json.get('username', '')}) or {}
        #     if 'token' not in user or user['token'] != request.json.get('token'):
        #         raise Unauthorized()

    # noinspection PyUnusedLocal
    @app.route('/favicon.ico')
    async def favicon(request: Request) -> HTTPResponse:
        return json_response('Favicon not found.', 404)

    # noinspection PyUnusedLocal
    @app.exception(ServerException)
    async def handle_server_error(request: Request, error: ServerException) -> HTTPResponse:
        return json_response(error.msg, error.status_code, error.errors)

    # noinspection PyUnusedLocal
    @app.exception(Exception)
    async def handle_error(request: Request, error: Exception) -> HTTPResponse:
        return json_response('Interval server error.', 500)

    enable_cors(app)

    return app
