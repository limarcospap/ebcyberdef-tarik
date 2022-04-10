import asyncio
from ..config import Config
from ..response import json_response
from ..exceptions import InvalidInputs
from .schemas import SearchLogs, GetLog, FinishLog, AddLog
from .helper import get_http_result, get_tor_result, get_whois_result, get_geolocation_result, parse_log_response
from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, json


logs_api = Blueprint('logs_api', url_prefix='/api/logs')


@logs_api.route('/search-logs', methods=['POST'])
async def search_logs(request: Request) -> HTTPResponse:
    data, error = SearchLogs().load(request.json)
    if not error:
        response = []
        query = {}
        if data['status']:
            query.update({'status': {'$in': data['status']}})
        if data['categories']:
            query.update({'category': {'$in': data['categories']}})
        documents = Config.current.logs.collection.find(query).limit(data['limit']).skip(data['skip']).sort([
            ('status_modified_at', 1)])
        async for document in documents:
            response.append(document)
        total = await Config.current.logs.collection.count_documents(query) if query else \
            await Config.current.logs.collection.estimated_document_count()
        return json({'logs': response, 'total': total})
    raise InvalidInputs()


@logs_api.route('/get-log', methods=['POST'])
async def get_log(request: Request) -> HTTPResponse:
    data, error = GetLog().load(request.json)
    if not error:
        response = await Config.current.logs.get(data['log_id'], 'admin')
        if response['category'] == 'DNS':
            response.update(get_whois_result(response['content']))
            tasks = [get_http_result(response['Host Name'])]
            if 'IP' in response:
                tasks.append(get_tor_result(response['IP']))
                tasks.append(get_geolocation_result(response['IP']))
            responses = await asyncio.gather(*tasks)
            for index in range(3):
                response.update(responses[index])
        return json(parse_log_response(response))
    raise InvalidInputs()


@logs_api.route('/add-dns-log', methods=['POST'])
async def add_dns_log(request: Request) -> HTTPResponse:
    data, error = AddLog().load(request.json)
    if not error:
        content = data['content'].split(' ')
        return json_response(await Config.current.logs.add('DNS', data['content'], domain=content[3]))
    raise InvalidInputs()


@logs_api.route('/finish-log', methods=['POST'])
async def finish_log(request: Request) -> HTTPResponse:
    data, error = FinishLog().load(request.json)
    if not error:
        return json_response(await Config.current.logs.finish(data['log_id'], data['status']))
    raise InvalidInputs()
