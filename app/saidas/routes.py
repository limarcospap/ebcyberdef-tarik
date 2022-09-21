import asyncio
from ..config import Config
from ..response import json_response
from ..exceptions import InvalidInputs
from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, json
from sanic.log import logger

saidas_api = Blueprint('saidas_api', url_prefix='/api/saidas')

@saidas_api.route('/get', methods=['GET'])
async def get(request : Request) -> HTTPResponse:
    documents = await Config.current.saidas.get_all()
    return json_response(documents, status=200)
