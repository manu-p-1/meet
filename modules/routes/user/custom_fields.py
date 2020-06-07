from wtforms import TextAreaField


class ISimpleEmployee:
    def __init__(self, eid, name=None):
        self.eid = eid
        self.name = name

    def __str__(self):
        return f"""
            "id": {self.eid}
            "name": {self.name}
        """


class EmployeeInfoTextAreaField(TextAreaField):
    def __init__(self, label='', validators=None, **kwargs):
        super(EmployeeInfoTextAreaField, self).__init__(label, validators, **kwargs)

    # noinspection PyTypeChecker
    def process_formdata(self, valuelist):
        super(EmployeeInfoTextAreaField, self).process_formdata(valuelist)

        if self.data is not None or self.data != '':
            self.data = self.scrub(self.data)

    @classmethod
    def scrub(cls, material):
        singled = material.strip().replace("\n", '').replace("\r", '')
        sub = singled.replace("NAME:", '').replace("ID: ", '-')
        splitted = sub.split("-")
        if len(splitted) == 1:
            return ''
        return ISimpleEmployee(eid=int(splitted[1]), name=splitted[0].strip())

