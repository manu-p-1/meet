import enum


class ManipulationType(enum.Enum):
    UPDATED = 'updated'
    DELETED = 'deleted'
    CREATED = 'created'


class OperationType(enum.Enum):
    ADD_EMPLOYEE = 'add'
    DELETE_EMPLOYEE = 'del'
