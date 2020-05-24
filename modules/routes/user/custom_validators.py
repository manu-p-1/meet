import sys
import pytz
from datetime import datetime, timezone, timedelta
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
    fmt = "%Y-%m-%d %H:%M:%S"

    def __init__(self, message=None):
        if not message:
            message = f'Date range is malformed. Follow the format YYYY-MM-DD HH:MM.'
        else:
            message = message + " Follow the format YYYY-MM-DD HH:MM. Hour's are in 24-hour format."
        self.message = message

    def __call__(self, form, field):
        self.timeZone = form.timeZone.data
        if type(field) is not StringField:
            raise ValidationError(self.message)

        if field.data is None:
            raise Exception('no field named "%s" in form' % field)

        field.data += ":00"
        print("FIELD SHORT NAME", field.short_name, file=sys.stderr)
        print("FIELD BEFORE CONVERT", field.data, file=sys.stderr)

        dtobj = self.check_field(field.data)

        """
        Choose the function depending on what kind of date it is 
        """
        if field.short_name == 'startDate':
            field.data = self.normalize_start(dtobj)
        else:
            field.data = self.normalize_end(dtobj)

        print("FIELD AFTER CONVERT", field.data, file=sys.stderr)

    def check_field(self, against):
        """
        Check if the date is valid, otherwise return a validation error
        :param against: The date as a string to be checked
        :return: a datetime object otherwise raise a ValidationError
        """
        try:
            naive = datetime.strptime(against, self.fmt)
            return naive
        except ValueError as ve:
            raise ValidationError(message=self.message)

    def normalize_start(self, dtobj):
        """

        Given a start date time as a datetime object, we make sure that the time the user
        submitted is between the current utc time and the current utc time - 1 hour

        If the plan start time on the form is older than 1 hour before the current UTC time:
            -> Send a Request Timeout

        If the plan start time is between the current utc time and 1 hour before the current UTC time:
            -> Adjust the plan start time to the current UTC time

        If the plan start time is ahead of the current utc time (future plan):
            -> Do nothing - convert it to a string with strftime


        :param dtobj: The datetime object representing the normalized start time
        :return: A string value of the UTC converted time, or a ValidationError otherwise
        """
        utc_dt = self.normalize(dtobj)

        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        one_hour_back = now - timedelta(hours=1)

        if utc_dt <= one_hour_back:
            raise ValidationError("The request timed out.")
        elif now >= utc_dt >= one_hour_back:
            return now.strftime(self.fmt)
        return utc_dt.strftime(self.fmt)

    def normalize_end(self, dtobj):
        """
        Given an end time as a datetime object, we make sure that the end date is not greater
        than 5 years from now. We put a cap that a plan cannot last more than 5 years.

        :param dtobj: The datetime object representing the normalized end time
        :return: A string value of the UTC converted time, or a ValidationError otherwise
        """
        utc_dt = self.normalize(dtobj)
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        five_years_fw = now + timedelta(days=1825)

        if utc_dt > five_years_fw:
            raise ValidationError("A plan can only extend for a maximum of 5 years.")

        return utc_dt.strftime(self.fmt)

    def normalize(self, dtobj):
        """
        Returns the current UTC time given a datetime object and its time zone.
        Converts the local time of the client that submitted into UTC
        :param dtobj:
        :return:
        """
        local = pytz.timezone(self.timeZone)
        local_dt = local.localize(dtobj, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)

        return utc_dt


class DeptBalance(object):
    def __init__(self, message=None, client=None, sn=None, employee_field=False):
        if not message:
            message = f'Funding amount is greater than the current department balance.'
        self.message = message
        self.client = client
        self.sn = sn
        self.employee_field = employee_field

    def __call__(self, form, field):
        if self.employee_field:
            if not valid_balance(client=self.client, sn=self.sn, field=field, field_len=len(field)):
                pass
        elif not valid_balance(client=self.client, sn=self.sn, field=field):
            raise ValidationError(self.message)


def valid_balance(client, sn, field, field_len=None) -> bool:
    dept_balance = client.retrieve_balance(
        client.DEPARTMENT_TOKEN_TO_OBJECTS[sn['manager_dept']]).gpa.available_balance * .8

    if field_len:
        if (field_len * sn['form_balance']) > dept_balance:
            return False
        else:
            return True
    else:
        sn['form_balance'] = field.data
        if field.data > dept_balance:
            return False
        else:
            return True