import hashlib
from . import exceptions
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# noinspection PyProtectedMember
from motor.motor_asyncio import AsyncIOMotorCollection


class Saida:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_all(self) -> list:
        result = list([])
        documents = await self.collection.find({}).to_list(length=100)
        for document in documents:
            document['_id'] = str(document['_id'])
            result.append(document)
        return result
