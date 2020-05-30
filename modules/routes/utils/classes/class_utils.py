import enum


class ManipulationType(enum.Enum):
    UPDATED = 'updated'
    DELETED = 'deleted'
    CREATED = 'created'


class OperationType(enum.Enum):
    ADD_EMPLOYEE = 'add'
    DELETE_EMPLOYEE = 'del'


class SupportedTimeFormats:
    FMT_UTC = "%Y-%m-%d %H:%M:%S"
    FMT_UI = "%m/%d/%Y %I:%M %p"
