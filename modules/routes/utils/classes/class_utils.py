import enum


class ManipulationType(enum.Enum):
    UPDATED = 'updated'
    DELETED = 'deleted'
    CREATED = 'created'
