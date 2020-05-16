from sys import stderr

from wtforms import FieldList, StringField
from wtforms.validators import Optional, DataRequired, ValidationError

from modules.routes.user.custom_fields import EmployeeInfoTextAreaField
from modules.routes.user.parsers import MRCDateRangeParser, MRCDateRangeException


class RequiredIf(DataRequired):

    def __init__(self, other_field_name, message=None):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(message=message)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field.data is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)

        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)
        else:
            Optional().__call__(form, field)


class Unique(object):
    def __init__(self, message=None, object_name='field values'):
        if not message:
            message = f'Duplicate {object_name} are not allowed.'
        self.message = message

    def __call__(self, form, fields):

        if type(fields) is not FieldList:
            raise Exception("Unique cannot be used on a non-FieldList type")

        if fields.data is None:
            raise Exception('no field named "%s" in form' % fields)

        if len(fields) == 0 or len(fields) == 1:
            return False

        no = self.has_dup(fields)
        if no:
            raise ValidationError(self.message)

    def has_dup(self, list_):
        seen = set()
        for x in list_:
            if x.data in seen:
                return True
            seen.add(x.data)
        return False


class EmployeeUnique(object):
    def __init__(self, message=None, object_name="employee id's"):
        if not message:
            message = f'Duplicate {object_name} are not allowed.'
        self.message = message

    def __call__(self, form, fields):

        if type(fields) is not FieldList:
            raise Exception("Unique cannot be used on a non-FieldList type")

        if fields.data is None:
            raise Exception('no field named "%s" in form' % fields)

        if len(fields) == 0 or len(fields) == 1:
            return False

        no = self.has_dup(fields)
        if no:
            raise ValidationError(self.message)

    def has_dup(self, list_):
        seen = set()
        for f in list_:

            if type(f) is not EmployeeInfoTextAreaField:
                raise Exception("EmployeeUnique cannot be used with a non EmployeeInfoTextAreaField type")

            if f.data['id'] in seen:
                return True
            seen.add(f.data['id'])
        return False


class DateRange(object):
    def __init__(self, message=None):
        if not message:
            message = f'Date range is malformed. Follow the format MM/DD/YYYY HH:MM PM - MM/DD/YYYY HH:MM AM'
        self.message = message

    def __call__(self, form, field):
        if type(field) is not StringField:
            raise ValidationError(self.message)

        if field.data is None:
            raise Exception('no field named "%s" in form' % field)

        drp = MRCDateRangeParser(field.data)

        try:
            drp.parse()
        except MRCDateRangeException as mrcdre:
            raise ValidationError(self.message)
