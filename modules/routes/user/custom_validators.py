import sys
from datetime import datetime, timezone
from wtforms import FieldList, StringField
from wtforms.validators import Optional, DataRequired, ValidationError
from modules.routes.user.custom_fields import EmployeeInfoTextAreaField


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


class DateProper(object):
    def __init__(self, message=None):
        if not message:
            message = f'Date range is malformed. Follow the format YYYY-MM-DD HH:MM:SS.'
        else:
            message = message + " Follow the format YYYY-MM-DD HH:MM:SS. Hour's are in 24-hour format."
        self.message = message

    def __call__(self, form, field):
        if type(field) is not StringField:
            raise ValidationError(self.message)

        if field.data is None:
            raise Exception('no field named "%s" in form' % field)
        print("FIELDDATA", field.data, file=sys.stderr)
        try:
            datetime.strptime(field.data, "%Y-%m-%d %H:%M:%S")
        except ValueError as ve:
            raise ValidationError(self.message)


class Active(object):
    def __init__(self, message=None, mysql=None):
        if not message:
            message = f'Requested plan is not active.'
        self.message = message
        self.mysql = mysql

    def __call__(self, form, field):
        if is_active(self.mysql, field):
            raise ValidationError(message=self.message)


class NotDuplicate(object):
    def __init__(self, message=None, mysql=None):
        if not message:
            message = f'Plan name is already in use.'
        self.message = message
        self.mysql = mysql

    def __call__(self, form, field):
        if is_duplicate(self.mysql, field):
            raise ValidationError(self.message)


def is_duplicate(mysql, field) -> bool:
    conn = mysql.connect()
    cursor = conn.cursor()
    q = '''SELECT plan_name FROM plan WHERE plan_name = %s'''
    cursor.execute(q, field)
    if len(cursor.fetchall()) == 0:
        return False
    else:
        return True


def is_active(mysql, field) -> bool:
    conn = mysql.connect()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)
    start_date = now.strftime("%Y-%m-%d %H:%M:%S")
    q = '''SELECT plan_name FROM plan WHERE plan_name = %s AND start_date > %s'''
    cursor.execute(q, (field, start_date))
    if len(cursor.fetchall()) == 0:
        return False
    else:
        return True
