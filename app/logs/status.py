from enum import Enum


class LogStatus(Enum):

    VALID = 'valid'
    DANGER = 'danger'
    PENDING = 'pending'
    WARNING = 'warning'
    PROCESSING = 'processing'
    INCONCLUSIVE = 'inconclusive'
