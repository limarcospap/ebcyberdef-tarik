import hashlib
from . import exceptions
from .messages import LogMessages
from .status import LogStatus
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# noinspection PyProtectedMember
from motor.motor_asyncio import AsyncIOMotorCollection


class Log:

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
        # noinspection PyTypeChecker
        self.valid_status = list(map(lambda x: x.value, LogStatus))
        self.valid_status.remove('pending')
        self.valid_status.remove('processing')

    async def add(self, category: str, content: str, **kwargs) -> str:
        log_id = hashlib.sha256((category + content).encode()).hexdigest()
        document = {'_id': log_id, 'category': category, 'content': content, 'status': LogStatus.PENDING.value,
                    'status_modified_at': datetime.utcnow(), **kwargs}
        try:
            await self.collection.insert_one(document)
            return LogMessages.LogAddSuccessfully
        except DuplicateKeyError:
            raise exceptions.LogAlreadyExists(log_id)

    async def get(self, log_id: str, worker_id: str) -> dict:
        update_to = {'status': LogStatus.PROCESSING.value, 'taken_by': worker_id, 'started_at': datetime.utcnow(),
                     'status_modified_at': datetime.utcnow()}
        job = await self.collection.find_one_and_update({'_id': log_id}, {'$set': update_to, '$inc': {'tries': 1}},
                                                        return_document=True)
        if not job:
            raise exceptions.LogNotFound(log_id)
        return job

    async def finish(self, log_id: str, status: str) -> str:
        update_to = {'status': status, 'status_modified_at': datetime.utcnow()}
        if status not in self.valid_status:
            raise exceptions.InvalidStatus(status)
        response = await self.collection.update_one({'_id': log_id}, {'$set': update_to})
        if not response.matched_count:
            raise exceptions.LogNotFound(log_id)
        return LogMessages.LogFinishedSuccessfully
