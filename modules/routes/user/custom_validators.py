import pytz
from datetime import datetime, timedelta
from wtforms import FieldList, StringField, RadioField
from wtforms.validators import Optional, DataRequired, ValidationError
from modules.routes.user.custom_fields import EmployeeInfoTextAreaField
from modules.routes.utils.classes.class_utils import SupportedTimeFormats


class RequiredIf(DataRequired):

    def __init__(self, other_field_name, message=None):
        self.other_field_name = other_field_name

        if message is None:
            message = "One ore more required Fields were missing"

        super(RequiredIf, self).__init__(message=message)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field.data is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)

        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)
        else:
            Optional().__call__(form, field)


class RequiredIfRadioField(DataRequired):

    def __init__(self, radio_field, radio_choice, message=None):
        self.radio_field = radio_field
        self.radio_choice = radio_choice

        if message is None:
            message = "One ore more required Fields were missing"

        super(RequiredIfRadioField, self).__init__(message=message)

    def __call__(self, form, field):
        rfld = form._fields.get(self.radio_field)

        if type(rfld) is not RadioField:
            raise Exception(f'{rfld} cannot be used with {self.__class__.__name__}')

        if rfld.data is None or rfld.data == self.radio_choice:
            super(RequiredIfRadioField, self).__call__(form, field)
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

            if f.data.eid in seen:
                return True
            seen.add(f.data.eid)
        return False


class StartDateProper:
    def __init__(self, message=None):
        if not message:
            message = f'Start date is malformed. Follow the format MM/DD/YYYY hh:mm AM[or PM].'
        self.message = message

    def __call__(self, form, field):
        dp = DateProper(field, form.time_zone.data, self.message)
        dtobj = dp.check_and_convert(field.data)
        start_obj = dp.normalize_start(dtobj)
        field.data = start_obj.strftime(SupportedTimeFormats.FMT_UTC)


class EndDateProper:
    def __init__(self, message=None):
        if not message:
            message = f'End date is malformed. Follow the format MM/DD/YYYY hh:mm AM[or PM].'
        self.message = message

    def __call__(self, form, field):
        dp = DateProper(field, form.time_zone.data, self.message)
        dtobj = dp.check_and_convert(field.data)
        end_obj: datetime = dp.normalize_end(dtobj)

        # 1 Hour from Start date - Do this in UTC because start date is processed first
        start_plus_one = datetime.strptime(form.start_date.data, SupportedTimeFormats.FMT_UTC) + timedelta(hours=1)

        if end_obj.replace(tzinfo=None) < start_plus_one:
            raise ValidationError(f'End date must be at least 1 hour ahead of the start date')

        field.data = end_obj.strftime(SupportedTimeFormats.FMT_UTC)


class DateProper(object):

    def __init__(self, field, timezone, message):
        self.timezone = timezone
        self.message = message

        if type(field) is not StringField:
            raise ValidationError(self.message)

        if field.data is None:
            raise Exception('no field named "%s" in form' % field)

    def check_and_convert(self, against):
        """
        Check if the date is valid, otherwise return a validation error
        :param against: The date as a string to be checked
        :return: a datetime object otherwise raise a ValidationError
        """
        try:
            return datetime.strptime(against, SupportedTimeFormats.FMT_UI)
        except ValueError:
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

        return utc_dt

    def normalize_end(self, dtobj):
        """
        Given an end time as a datetime object, we make sure that the end date is not greater
        than 5 years from now. We put a cap that a plan cannot last more than 5 years.
        :param dtobj: The datetime object representing the normalized end time
        :return: A string value of the UTC converted time, or a ValidationError otherwise
        """
        utc_dt = self.normalize(dtobj)
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        five_years_fw = now + timedelta(days=1825)  # Five years

        if utc_dt > five_years_fw:
            raise ValidationError("A plan can only extend for a maximum of 5 years.")

        return utc_dt

    def normalize(self, dtobj):
        """
        Returns the current UTC time given a datetime object and its time zone.
        Converts the local time of the client that submitted into UTC
        :param dtobj:
        :return:
        """
        local = pytz.timezone(self.timezone)
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
