import time
import whois
import socket
from ..config import Config
from .exceptions import WhoisError
# noinspection PyProtectedMember
from concurrent.futures._base import TimeoutError
from datetime import datetime


async def get_tor_result(ip: str) -> dict:
    url = 'https://check.torproject.org/cgi-bin/TorBulkExitList.py?ip=1.1.1.1'
    if not Config.current.tor_list['list'] or (datetime.utcnow() - Config.current.tor_list['date']).seconds > 3600:
        response = await Config.current.requests.get(url)
        Config.current.tor_list['list'] = (await response.read()).decode().split('\n')[3:-1]
    return {'Tor': 'True' if ip in Config.current.tor_list['list'] else 'False'}


async def get_geolocation_result(ip: str) -> dict:
    result = {}
    url = f'https://api.ipgeolocation.io/ipgeo?apiKey={Config.current.apikey}&ip={ip}'
    whitelist = ['country_name', 'country_code3', 'region_name', 'region_code', 'city', 'continent_name', 'state_prov',
                 'zipcode', 'latitude', 'longitude', 'country_tld']
    response = await (await Config.current.requests.get(url)).json()
    for word in whitelist:
        if response.get(word):
            result[word] = response.get(word)
    if not result:
        result['GeoLocation'] = 'Limit Exceeded (1000/day)'
    return result


async def get_http_result(domain: str) -> dict:
    result = {}
    t = time.time()
    try:
        response = await Config.current.requests.get(f'http://{domain}', timeout=30)
        result['Response Time'] = f'{round(time.time() - t, 3)}s'
        result['URL'] = response.url.human_repr()
        result['Status'] = response.status
        result['Content Type'] = response.content_type
        result['Content Length'] = response.content_length or 'Undefined'
    except TimeoutError:
        result['Status'] = 'Connection Failed, 30s Timeout'
    return result


def get_whois_result(content: str) -> dict:
    result = {}
    content = content.split(' ')
    try:
        result['IP'] = socket.gethostbyname(content[3])
    except socket.gaierror:
        raise WhoisError
    result['Host Name'] = content[3]
    result.update(get_whois_info(content[3]))
    result['Client IP'] = content[1]
    try:
        result['Client Host'] = socket.gethostbyaddr(content[1])[0]
    except socket.herror:
        pass
    result['Client Port'] = content[2]
    result['DNS Type'] = content[4]
    result['DNS Flags'] = content[5]
    result['DNS Recursion'] = 'Available' if '+' in content[5] else 'Unavailable'
    result['Log Date'] = content[0]
    return result


def get_whois_info(domain: str) -> dict:
    data = {}
    whitelist = ['Domain Name', 'Updated Date', 'Creation Date', 'Registry Expiry Date', 'DNSSEC',
                 'Registrar Registration Expiration Date', 'Registrant Name', 'Registrant Street', 'Registrant City',
                 'Registrant State/Province', 'Registrant Country', 'Admin Name', 'Admin Street', 'Admin City',
                 'Admin State/Province', 'Admin Country']
    result = whois.whois(domain).__dict__
    data['Domain'] = result['domain']
    for info in result['text'].split('\n'):
        parsed_info = info.strip().split(': ')
        if parsed_info[0] in whitelist:
            parsed_info = info.strip().split(': ')
            if len(parsed_info) == 2:
                data[parsed_info[0]] = parsed_info[1]
    return data


def get_years_elapsed(value: str) -> int:
    return datetime.utcnow().year - datetime.strptime(value[:-1], "%Y-%m-%dT%H:%M:%S").year


def parse_log_response(data: dict) -> dict:
    parsed_data = {"General": [], "HTTP": [], "Location": [], "DNS": [], "Register": [], "Admin": []}
    for key, value in data.items():
        try:
            new_data = {"value": value, "result": None, "key": key}
            if key in {"IP", "Host Name", "Domain", "Log Date", "Client IP", "Client Host", "Client Port"}:
                group = "General"
            elif key == "Updated Date":
                group = "Register"
                value = value[:19]
                new_data["value"] = value
                new_data["result"] = "success" if get_years_elapsed(value) < 3 else "danger"
            elif key == "Creation Date":
                value = value[:19]
                new_data["value"] = value
                group = "Register"
                new_data["result"] = "success" if get_years_elapsed(value) > 3 else "danger"
            elif key == "Registry Expiry Date":
                value = value[:19]
                new_data["value"] = value
                group = "Register"
                new_data["key"] = "Expiry Date"
                new_data["result"] = "success" if get_years_elapsed(value) < -2 else "danger"
            elif "Registrant" in key:
                group = "Register"
                new_data["key"] = key.split(" ")[1]
            elif "DNS" in key:
                group = "DNS"
                key = key.split(" ")
                new_data["key"] = key[1] if len(key) > 1 else key[0]
            elif "Admin" in key:
                group = "Admin"
                new_data["key"] = key.split(" ")[1]
            elif key == "Response Time":
                group = "HTTP"
                new_data["result"] = "success" if float(value[:-1]) < 0.5 else "danger"
            elif key == "URL":
                group = "HTTP"
            elif key == "Status":
                group = "HTTP"
                new_data["result"] = "success" if 200 <= value < 300 else "danger"
            elif key == "Content Type":
                group = "HTTP"
                new_data["result"] = "success" if value == "text/html" else "danger"
            elif key == "Content Length":
                group = "HTTP"
                new_data["result"] = "success" if value > 2500 else "danger"
            elif key == "Tor":
                group = "General"
                new_data["result"] = "success" if value else "danger"
            elif key == "country_code3":
                group = "Location"
                new_data["key"] = "Country Code"
                new_data["result"] = "danger" if value in {"USA", "CHN", "RUS"} else "success"
            elif key == "country_tld":
                group = "Location"
                new_data["key"] = "Top Domain"
                new_data["result"] = "danger" if value in {
                    ".gq", ".cf", ".tk", ".ml", ".ga", ".men", ".loan", ".date", ".tw", ".bid"} else "success"
            elif key == "country_name":
                group = "Location"
                new_data["key"] = "Country Name"
                new_data["result"] = "danger" if data["country_code3"] in {"USA", "CHN", "RUS"} else "success"
            elif key in ['region_name', 'region_code', 'city', 'continent_name', 'state_prov', 'zipcode', 'latitude',
                         'longitude']:
                group = "Location"
                new_data["key"] = " ".join(list(map(lambda x: x.capitalize(), key.split("_"))))
            else:
                continue
            parsed_data[group].append(new_data)
        except Exception as e:
            if group:
                new_data["result"] = "danger"
    if not parsed_data.get('Location'):
        parsed_data.pop('Location')
    return parsed_data
