from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, BooleanField, SubmitField, DecimalField, \
    FieldList
from wtforms.validators import InputRequired, NumberRange
from wtforms.widgets.html5 import NumberInput
from modules.routes.user.custom_validators import RequiredIf, Unique, DateRange


class CreatePlanForm(FlaskForm):
    planName = StringField("Plan Name", validators=[InputRequired()],
                           render_kw={"placeholder": "Plan Name",
                                      "class": "form-control"})

    fundingAmount = DecimalField('Funding Amount', validators=[InputRequired(), NumberRange(min=100.00)],
                                 render_kw={"placeholder": "Funding Amount",
                                            "class": "form-control"},
                                 widget=NumberInput())

    planJustification = StringField('Plan Justification (e.g. Travel, Equipment, Party)', validators=[InputRequired()],
                                    render_kw={"placeholder": "Plan Justification",
                                               "class": "form-control"})

    description = TextAreaField('Description (max 500 chars.)',
                                validators=[InputRequired()],
                                render_kw={"rows": 4,
                                           "maxlength": 500,
                                           "placeholder": "Description",
                                           "class": "form-control"})

    dateRange = StringField('Start and End Date/Times', validators=[InputRequired(), DateRange()],
                            render_kw={"placeholder": "Start and End Date/Times",
                                       "class": "form-control"})

    sourceFund = SelectField('Fund Source', validators=[InputRequired()],
                             choices=[
                                 ('', 'Destination Fund Department'),
                                 ('Professional Services', 'Professional Services')
                             ],
                             render_kw={"class": "form-control"},
                             default='')

    destFund = SelectField('Fund Destination', validators=[InputRequired()],
                           choices=[
                               ('Professional Services', 'Professional Services')
                           ],
                           render_kw={"class": "form-control"},
                           default='')

    fundIndivEmployeesToggle = BooleanField('Transfer funds to individual', default=False,
                                            render_kw={"class": "custom-control-input"})

    employeesOptional = FieldList(StringField('employeesOptional',
                                              validators=[
                                                  RequiredIf('fundIndivEmployeesToggle'),
                                              ],
                                              render_kw={"class": "employeeIDInput form-control position-relative",
                                                         "placeholder": "Enter Employee ID"}),
                                  validators=[Unique(object_name="employee id's")],
                                  min_entries=1,
                                  max_entries=12)

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

    amountLimit = DecimalField('Amount Limit', validators=[RequiredIf('controlToggle'), NumberRange(min=0.00)],
                               render_kw={"placeholder": "Amount Limit",
                                          "class": "form-control",
                                          },
                               widget=NumberInput())

    usageLimit = IntegerField('Usage Limit', validators=[RequiredIf('controlToggle'), NumberRange(min=0, max=100)],
                              render_kw={"placeholder": "Usage Limit",
                                         "class": "form-control",
                                         },
                              widget=NumberInput())

    createPlanButton = SubmitField("Create Plan", render_kw={"class": "btn btn-primary btn-block"})
