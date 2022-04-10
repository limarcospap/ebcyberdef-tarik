from .status import LogStatus
from marshmallow import Schema, fields, validate


class SearchLogs(Schema):

    skip = fields.Integer(required=True)
    limit = fields.Integer(required=True, validate=validate.Range(max=100))
    categories = fields.List(fields.String(validate=validate.OneOf(['DNS'])), required=True)
    # noinspection PyTypeChecker
    status = fields.List(fields.String(validate=validate.OneOf(list(map(lambda x: x.value, LogStatus))), required=True))


class GetLog(Schema):

    log_id = fields.String(required=True)


class AddLog(Schema):

    content = fields.String(required=True)


class FinishLog(GetLog):

    status = fields.String(required=True)
