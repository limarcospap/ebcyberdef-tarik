from .logs.log import Log
from .users.user import User
from datetime import datetime
from aiohttp import ClientSession
from cached_property import cached_property
from motor.motor_asyncio import AsyncIOMotorClient


class Config:

    current: 'Config' = None

    def __init__(self, loaded_config: dict):
        self.sanic = loaded_config['sanic']
        self.token = loaded_config['token']
        self.apikey = loaded_config['apikey']
        self.mongo_config = loaded_config['mongo']
        self.database = self.mongo_config.pop('database')
        self.collections = self.mongo_config.pop('collections')
        self.tor_list = {'list': [], 'date': datetime.utcnow()}

    def __new__(cls, *args, **kwargs):
        if not cls.current:
            cls.current = super().__new__(cls)
            return cls.current
        else:
            raise Exception("You can't create a new config instance.")

    @cached_property
    def requests(self) -> ClientSession:
        return ClientSession()

    @cached_property
    def logs(self) -> Log:
        return Log(AsyncIOMotorClient(**self.mongo_config)[self.database][self.collections["logs"]])

    @cached_property
    def users(self) -> User:
        return User(AsyncIOMotorClient(**self.mongo_config)[self.database][self.collections["users"]])
