from . import exceptions
from .messages import UserMessages
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from pymongo.errors import DuplicateKeyError
# noinspection PyProtectedMember
from motor.motor_asyncio import AsyncIOMotorCollection


class User:

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def register(self, username: str, email: str, password: str) -> str:
        document = {'_id': username, 'email': email, 'password': pbkdf2_sha256.hash(password),
                    'created_at': datetime.utcnow()}
        try:
            await self.collection.insert_one(document)
            return UserMessages.RegisterSuccessfully
        except DuplicateKeyError:
            raise exceptions.UserAlreadyExists(username)
