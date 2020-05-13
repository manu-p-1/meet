from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, BooleanField
from wtforms.validators import InputRequired, NumberRange, ValidationError, DataRequired
from sys import stderr


class RequiredIf(DataRequired):

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        print(other_field_name, file=stderr)
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        print(other_field, file=stderr)
        if other_field.data is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)


class Unique(object):
    def __init__(self, message=None):
        if not message:
            message = 'Duplicate field values are not allowed.'
        self.message = message

    def __call__(self, form, field: []):
        print(field, file=stderr)
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


class CreatePlanForm(FlaskForm):
    planName = StringField("Form Plan", validators=[InputRequired()],
                           render_kw={"placeholder": "Plan Name",
                                      "class": "form-control"})

    fundingAmount = IntegerField('Funding Amount', validators=[InputRequired(), NumberRange(min=100.00)],
                                 render_kw={"placeholder": "Funding Amount",
                                            "class": "form-control",
                                            "min": 100.00})

    planJustification = StringField('Plan Justification', validators=[InputRequired()],
                                    render_kw={"placeholder": "Plan Justification (e.g. Travel, Equipment, Party)",
                                               "class": "form-control"})

    description = TextAreaField('Description', validators=[InputRequired()],
                                render_kw={"rows": 4,
                                           "maxlength": 500,
                                           "placeholder": "Description",
                                           "class": "form-control"})

    activeRange = StringField('Start and End Date/Times', validators=[InputRequired()],
                              render_kw={"placeholder": "Start and End Date/Times",
                                         "class": "form-control"})

    sourceFund = SelectField('Source Fund', validators=[InputRequired()],
                             choices=[
                                 ('', 'Destination Fund Department'),
                                 ('Professional Services', 'Professional Services')
                             ],
                             render_kw={"class": "form-control"},
                             default='')

    destFund = SelectField('Source Fund', validators=[InputRequired()],
                           choices=[
                               ('Professional Services', 'Professional Services')
                           ],
                           render_kw={"class": "form-control"},
                           default='')

    fundIndivEmployeesToggle = BooleanField('Transfer funds to individual', default=False,
                                            render_kw={"class": "custom-control-input"})

    employeesOptional = StringField('Employees Optional',
                                    validators=[
                                        RequiredIf('fundIndivEmployeesToggle'),
                                        Unique()
                                    ],
                                    render_kw={"class": "employeeIDInput form-control position-relative",
                                               "placeholder": "Enter Employee ID"})

    controlToggle = BooleanField('Add Velocity Controls', default=False,
                                 render_kw={"class": "custom-control-input"})

    controlName = StringField('Control Name', validators=[RequiredIf('controlToggle')],
                              render_kw={"class": "form-control",
                                         "placeholder": "Enter a Control Name"})

    controlWindow = SelectField('Control Window', validators=[RequiredIf('controlToggle')],
                                choices=[
                                    ('', 'Select a Control Time Period'),
                                    ('day', 'DAY'),
                                    ('week', 'WEEK'),
                                    ('month', 'MONTH'),
                                    ('lifetime', 'LIFETIME'),
                                    ('transaction', 'TRANSACTION')
                                ],
                                render_kw={"class": "form-control"},
                                default='')

    amountLimit = IntegerField('Amount Limit', validators=[RequiredIf('controlToggle'), NumberRange(min=0.00)],
                               render_kw={"placeholder": "Amount Limit",
                                          "class": "form-control",
                                          "min": 0.00})

    usageLimit = IntegerField('Usage Limit', validators=[RequiredIf('controlToggle'), NumberRange(min=0, max=100)],
                              render_kw={"placeholder": "Usage Limit",
                                         "class": "form-control",
                                         "min": 0,
                                         "max": 100})
