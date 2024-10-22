import sys
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
        field.data = dp.normalize_start(dtobj)


class EndDateProper:
    def __init__(self, message=None):
        if not message:
            message = f'End date is malformed. Follow the format MM/DD/YYYY hh:mm AM[or PM].'
        self.message = message

    def __call__(self, form, field):
        dp = DateProper(field, form.time_zone.data, self.message)
        dtobj = dp.check_and_convert(field.data)

        # 1 Hour from Start date - Do this in UTC because start date is processed first
        start_plus_one = datetime.strptime(form.start_date.data, SupportedTimeFormats.FMT_UTC) + timedelta(hours=1)

        if dtobj < start_plus_one:
            raise ValidationError(f'End date must be at least 1 hour ahead of the start date')

        field.data = dp.normalize_end(dtobj)


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

        return utc_dt.strftime(SupportedTimeFormats.FMT_UTC)

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

        return utc_dt.strftime(SupportedTimeFormats.FMT_UTC)

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
    def __init__(self, client, sn, message=None):
        if not message:
            message = f'Funding amount is greater than the current department balance.'
        self.message = message
        self.client = client
        self.sn = sn

    def __call__(self, form, field):
        self.valid_balance(form=form, field=field)

    def valid_balance(self, form, field):
        dept_balance = float(self.client.retrieve_balance(
            self.client.DEPARTMENT_TOKEN_TO_OBJECTS[self.sn['manager_dept']].token).gpa.available_balance) * .8

        if dept_balance < 500:
            raise ValidationError(message="Department balance too low")

        if form.disbursement_type.data == form.DISB_INDIV:
            num_employees = len(form.employees_list)
            total = field.data * num_employees

            if total > dept_balance:
                raise ValidationError(self.message)

        elif form.disbursement_type.data == form.DISB_ALL:

            # Hard coded because this is a hackathon
            num_employees = 12
            total = field.data * num_employees

            if total > dept_balance:
                raise ValidationError(self.message)
        else:
            if field.data > dept_balance:
                raise ValidationError(self.message)


class VelocityUsageLimit:
    def __init__(self, message=None):
        if not message:
            message = f'The velocity control usage limit must be less than the plan funding amount.'
        self.message = message

    def __call__(self, form, field):
        if field.data > form.funding_amount.data:
            raise ValidationError(self.message)