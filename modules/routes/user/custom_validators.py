from sys import stderr

from wtforms import FieldList, StringField
from wtforms.validators import Optional, DataRequired, ValidationError


class RequiredIf(DataRequired):

    def __init__(self, other_field_name):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__()

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field.data is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)

        print("Field", field, "\nType: ", type(field), file=stderr)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)
        else:
            Optional().__call__(form, field)


class Unique(object):
    def __init__(self, message=None, object_name='field values'):
        if not message:
            message = f'Duplicate {object_name} are not allowed.'
        self.message = message

    def __call__(self, form, field):

        print("Field", field, "\nType: ", type(field), file=stderr)
        if type(field) is FieldList:
            no = self.has_dup(field)
            if no:
                raise ValidationError(self.message)

    def has_dup(self, list_):
        seen = set()
        for x in list_:
            if x.data in seen:
                return True
            seen.add(x.data)
        return False


class DateRange(object):
    def __init__(self, message=None):
        if not message:
            message = f'Range is malformed. Follow the format MM/DD/YYYY HH:MM AM/PM - MM/DD/YYYY HH:MM AM/PM'
        self.message = message

    def __call__(self, form, field):
        print("Field", field, "\nType: ", type(field), file=stderr)
        print(field.data, file=stderr)
        # daterange = str(field.data)
        #
        # if type(field) is not StringField:
        #     raise ValidationError(self.message)
        #
        # splitted = daterange.split("-")
        #
        # start_range = splitted[0]
        # end_range = splitted[1]
        #
        # print(start_range, file=stderr)
        # print(end_range, file=stderr)


class DateParser:
    pass
