from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, BooleanField, SubmitField, DecimalField, \
    FieldList
from wtforms.validators import InputRequired, NumberRange, Length
from wtforms.widgets.html5 import NumberInput

from modules.routes.user.custom_fields import EmployeeInfoTextAreaField
from modules.routes.user.custom_validators import RequiredIf, DateProper, EmployeeUnique


class CreatePlanForm(FlaskForm):
    planName = StringField("Plan Name", validators=[InputRequired(message="Enter a plan name.")],
                           render_kw={"placeholder": "Plan Name",
                                      "class": "form-control"})

    fundingAmount = DecimalField('Funding Amount',
                                 validators=[
                                     InputRequired(message="Enter a funding amount."),
                                     NumberRange(min=100.00,
                                                 message="The minimum funding amount must be at least $100.00.")
                                 ],
                                 render_kw={"placeholder": "Funding Amount",
                                            "class": "form-control"},
                                 widget=NumberInput())

    planJustification = StringField('Plan Justification (e.g. Travel, Equipment, Party)',
                                    validators=[
                                        InputRequired(message="A plan justification is required."),
                                        Length(min=3, message="Please enter a meaningful justification.")
                                    ],
                                    render_kw={"placeholder": "Plan Justification",
                                               "class": "form-control"})

    description = TextAreaField('Description (min 10 chars, max 500 chars.)',
                                validators=[
                                    InputRequired("A description is required."),
                                    Length(min=10, max=500, message="Description was either too short or too long.")
                                ],
                                render_kw={"rows": 4,
                                           "maxlength": 500,
                                           "placeholder": "Description",
                                           "class": "form-control"})

    startDate = StringField('Start Date/Times',
                            validators=[
                                InputRequired(message="A start date is required."),
                                DateProper(message="The start date is malformed.")
                            ],
                            render_kw={"placeholder": "Start Date/Times",
                                       "class": "form-control"})

    sourceFund = SelectField('Fund Source',
                             validators=[InputRequired(message="A funding source department is required.")],
                             choices=[
                                 ('Professional Services', 'Professional Services')
                             ],
                             render_kw={"class": "form-control"},
                             default='')

    destFund = SelectField('Fund Destination',
                           validators=[InputRequired(message="A funding destination department is required.")],
                           choices=[
                               ('', 'Destination Fund Department'),
                               ('ACCOUNTING', 'ACCOUNTING')
                           ],
                           render_kw={"class": "form-control"},
                           default='')

    fundIndivEmployeesToggle = BooleanField('Employee specific disbursement', default=False,
                                            render_kw={"class": "custom-control-input"})

    employeesOptional = FieldList(EmployeeInfoTextAreaField('employeesOptional',
                                                            validators=[
                                                                RequiredIf('fundIndivEmployeesToggle',
                                                                           message="Please specify at least 1 "
                                                                                   "employee to disburse funds to."),
                                                            ]),
                                  validators=[EmployeeUnique(object_name="employee id's")],
                                  min_entries=1,
                                  max_entries=12)

    endDateToggle = BooleanField('Add End Date', default=False, render_kw={"class": "custom-control-input"})

    endDate = StringField('End Date/Times',
                          validators=[
                              RequiredIf("endDateToggle", message="The end date is required."),
                              DateProper(message="The end date is malformed.")
                          ],
                          render_kw={"placeholder": "Date Date/Times",
                                     "class": "form-control"})

    controlToggle = BooleanField('Add Velocity Controls', default=False,
                                 render_kw={"class": "custom-control-input"})

    controlName = StringField('Control Name',
                              validators=[
                                  RequiredIf('controlToggle',
                                             message="The velocity control, control name is required.")
                              ],
                              render_kw={"class": "form-control",
                                         "placeholder": "Enter a Control Name"})

    controlWindow = SelectField('Control Window',
                                validators=[
                                    RequiredIf('controlToggle',
                                               message="The velocity control, control window is required.")
                                ],
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

    amountLimit = DecimalField('Amount Limit',
                               validators=[
                                   RequiredIf('controlToggle',
                                              message="The velocity control amount limit is required."),
                                   NumberRange(min=100.00,
                                               message="The minimum velocity control amount limit must be at least "
                                                       "$100.00.")
                               ],
                               render_kw={"placeholder": "Amount Limit",
                                          "class": "form-control",
                                          },
                               widget=NumberInput())

    usageLimit = IntegerField('Usage Limit',
                              validators=[
                                  RequiredIf('controlToggle', message="The velocity control usage limit is required."),
                                  NumberRange(min=0, max=100,
                                              message="The velocity control usage limit should be between 0 and 100, "
                                                      "inclusive.")
                              ],
                              render_kw={"placeholder": "Usage Limit",
                                         "class": "form-control",
                                         },
                              widget=NumberInput())

    createPlanButton = SubmitField("Create Plan", render_kw={"class": "btn btn-primary btn-block"})
