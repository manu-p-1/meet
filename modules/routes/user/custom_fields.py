import sys

from wtforms import TextAreaField


class EmployeeInfoTextAreaField(TextAreaField):
    def __init__(self, label='', validators=None, **kwargs):
        super(EmployeeInfoTextAreaField, self).__init__(label, validators, **kwargs)

    # noinspection PyTypeChecker
    def process_formdata(self, valuelist):
        super(EmployeeInfoTextAreaField, self).process_formdata(valuelist)

        if self.data is not None or self.data != '':
            self.data = self.scrub(self.data)
            print("EMPLOYEE FIELD DATA:", self.data, file=sys.stderr)

    @classmethod
    def scrub(cls, material):
        singled = material.strip().replace("\n", '').replace("\r", '')
        sub = singled.replace("NAME:", '').replace("ID: ", '-')
        splitted = sub.split("-")
        if len(splitted) == 1:
            return ''
        return {
            "id": int(splitted[1]),
            "name": splitted[0].strip()
        }
