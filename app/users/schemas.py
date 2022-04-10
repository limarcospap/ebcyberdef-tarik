from marshmallow import Schema, fields


class Username(Schema):

    username = fields.String(required=True)


class LogIn(Username):

    password = fields.String(required=True)


class Register(LogIn):

    email = fields.Email(required=True)
    token = fields.String(required=True)
