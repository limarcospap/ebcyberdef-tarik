import uuid
from ..config import Config
from ..response import json_response
from ..exceptions import InvalidInputs
from .messages import UserMessages
from .schemas import Register, LogIn, Username
from .exceptions import InvalidToken, UserNotFound, InvalidPassword
from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse
from passlib.hash import pbkdf2_sha256


users_api = Blueprint('users_api', url_prefix='/api/users')


@users_api.route('/register', methods=['POST'])
async def register(request: Request) -> HTTPResponse:
    data, error = Register().load(request.json)
    if not error:
        if data['token'] != Config.current.token:
            raise InvalidToken()
        return json_response(await Config.current.users.register(data['username'], data['email'], data['password']))
    raise InvalidInputs()


@users_api.route('/login', methods=['POST'])
async def login(request: Request) -> HTTPResponse:
    data, error = LogIn().load(request.json)
    if not error:
        user = await Config.current.users.collection.find_one({'_id': data['username']})
        if not user:
            raise UserNotFound(data['username'])
        if not pbkdf2_sha256.verify(data['password'], user['password']):
            raise InvalidPassword()
        token = uuid.uuid4().hex
        await Config.current.users.collection.update_one({'_id': data['username']}, {'$set': {'token': token}})
        return json_response(UserMessages.LogInSuccessfully, token=token, username=data['username'])
    raise InvalidInputs()


@users_api.route('/logout', methods=['POST'])
async def logout(request: Request) -> HTTPResponse:
    data, error = Username().load(request.json)
    if not error:
        await Config.current.users.collection.update_one({'_id': data['username']}, {'$unset': {'token': ''}})
        return json_response(UserMessages.LogoutSuccessfully)
    raise InvalidInputs()
