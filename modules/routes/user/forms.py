from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, BooleanField, DecimalField, \
    FieldList, HiddenField, RadioField
from wtforms.validators import InputRequired, NumberRange, Length, AnyOf
from wtforms.widgets.html5 import NumberInput

from modules.routes.user.custom_fields import EmployeeInfoTextAreaField
from modules.routes.user.custom_validators import RequiredIf, EmployeeUnique, EndDateProper, \
    StartDateProper
from modules.routes.utils.custom_fields import InlineSubmitField

from server import client

DEPT_MAPPINGS = [
    ('', 'Please Choose a fund Destination'),
    ('IT', 'IT'), ('AC', 'ACCOUNTING'), ('MK', 'MARKETING'), ('HR', 'HUMAN RESOURCES'),
    ('PD', 'PRODUCTION'), ('RD', 'RESEARCH & DEVELOPMENT'), ('SC', 'SECURITY'), ('LG', 'LOGISTICS')
]


def create_plan_form(sn):
    """
    CREATE PLAN FORM
    :param sn: Session Dictionary
    :return: A Create Plan Form
    """

    class CreatePlanForm(get_plan_base(sn)):
        createPlanButton = InlineSubmitField("Create Plan", btn_text="Create Plan",
                                             render_kw={"class": "btn btn-primary btn-block"})

    return CreatePlanForm()


def get_plan_form(sn: dict):
    """
    GET PLAN FORM
    :param sn: Session Dictionary
    :return: A Manage Plan Form
    """

    class ManagePlanForm(get_plan_base(sn)):
        updatePlanButton = InlineSubmitField("Update Plan", btn_text="Update Plan",
                                             render_kw={"class": "btn btn-primary btn-block"})

    return ManagePlanForm()


def get_plan_base(sn: dict):
    """
    GET REFERENCE TO PLAN BASE FORM
    :param sn: Session Dictionary
    :return: A Plan Form
    """

    class Plan(FlaskForm):
        planName = StringField("Plan Name",
                               validators=[InputRequired(message="Enter a plan name.")],
                               render_kw={"placeholder": "Plan Name",
                                          "class": "form-control"})

        fundingAmount = DecimalField('Per-Employee Funding Amount',
                                     validators=[
                                         InputRequired(message="Enter a funding amount."),
                                         NumberRange(min=15.00,
                                                     message="The minimum funding amount must be at least $15.00.")
                                     ],
                                     render_kw={"placeholder": "Funding Amount",
                                                "class": "form-control"},
                                     widget=NumberInput())

        planJustification = StringField('Plan Justification (e.g. Travel, Equipment, Party)',
                                        validators=[
                                            InputRequired(message="A plan justification is required."),
                                            Length(min=3, max=50,
                                                   message="Plan justification was either too short or too long.")
                                        ],
                                        render_kw={"placeholder": "Plan Justification",
                                                   "class": "form-control"})

        memo = TextAreaField('Memo (min 10 chars, max 255 chars.)',
                             validators=[
                                 InputRequired("A memo is required."),
                                 Length(min=10, max=255, message="Memo was either too short or too long.")
                             ],
                             render_kw={"rows": 4,
                                        "maxlength": 255,
                                        "placeholder": "Memo Description",
                                        "class": "form-control"})

        startDate = StringField('Start Date/Times',
                                validators=[
                                    InputRequired(message="A start date is required."),
                                    StartDateProper()
                                ],
                                render_kw={"placeholder": "Start Date/Times",
                                           "class": "form-control"})

        sourceFund = SelectField('Fund Source',
                                 validators=[InputRequired(message="A funding source department is required.")],
                                 choices=[
                                     (
                                         sn['manager_dept'],
                                         client.READABLE_DEPARTMENTS[sn['manager_dept']]
                                     )
                                 ],
                                 render_kw={"class": "form-control"})

        destFund = SelectField('Fund Destination',
                               validators=[InputRequired(message="A funding destination department is required.")],
                               choices=DEPT_MAPPINGS,
                               render_kw={"class": "form-control"})

        fundIndivEmployeesToggle = BooleanField('Employee specific disbursement',
                                                render_kw={"class": "custom-control-input"})

        searchEmployee = RadioField('Search for an employee', render_kw={"class": "form-control custom-control-input"})

        allEmployees = RadioField('Disburse to all Employees', render_kw={"class": "form-control custom-control-input"})

        employeesOptional = FieldList(EmployeeInfoTextAreaField('employeesOptional',
                                                                validators=[
                                                                    RequiredIf('fundIndivEmployeesToggle',
                                                                               message="Please specify at least 1 "
                                                                                       "employee to disburse funds to."),
                                                                ]),
                                      validators=[EmployeeUnique(object_name="employee id's")],
                                      min_entries=1,
                                      max_entries=12)

        endDateToggle = BooleanField('Add End Date',
                                     render_kw={"class": "custom-control-input"})

        endDate = StringField('End Date/Times',
                              validators=[
                                  RequiredIf("endDateToggle", message="The end date is required."),
                                  EndDateProper(),
                              ],
                              render_kw={"placeholder": "Date Date/Times",
                                         "class": "form-control"})

        controlToggle = BooleanField('Add Velocity Controls',
                                     render_kw={"class": "custom-control-input"})

        controlName = StringField('Control Name',
                                  validators=[
                                      RequiredIf('controlToggle',
                                                 message="The velocity control, control name is required."),
                                      Length(max=50)
                                  ],
                                  render_kw={"class": "form-control",
                                             "placeholder": "Enter a Control Name"})

        controlWindow = SelectField('Control Window',
                                    validators=[
                                        RequiredIf('controlToggle',
                                                   message="The velocity control, control window is required."),
                                        Length(max=30)
                                    ],
                                    choices=[
                                        ('', 'Select a Control Time Period'),
                                        ('day', 'DAY'),
                                        ('week', 'WEEK'),
                                        ('month', 'MONTH'),
                                        ('lifetime', 'LIFETIME'),
                                        ('transaction', 'TRANSACTION')
                                    ],
                                    render_kw={"class": "form-control"})

        amountLimit = DecimalField('Amount Limit',
                                   validators=[
                                       RequiredIf('controlToggle',
                                                  message="The velocity control amount limit is required."),
                                       NumberRange(min=15.00,
                                                   message="The minimum velocity control amount limit must be at least "
                                                           "$15.00.")
                                   ],
                                   render_kw={"placeholder": "Amount Limit",
                                              "class": "form-control"},
                                   widget=NumberInput())

        usageLimit = IntegerField('Usage Limit (0 - 100)',
                                  validators=[
                                      RequiredIf('controlToggle',
                                                 message="The velocity control usage limit is required."),
                                      NumberRange(min=0, max=100,
                                                  message="The velocity control usage limit should be between "
                                                          "0 and 100, inclusive.")
                                  ],
                                  render_kw={"placeholder": "Usage Limit",
                                             "class": "form-control"},
                                  widget=NumberInput())

        timeZone = HiddenField(validators=[InputRequired(message="The timezone is a required field")])

        priority = HiddenField(validators=[
            InputRequired(message="Priority is a required field"),
            AnyOf(values=["Low", "Medium", "High", "Urgent"], message="Priority must be Low, Medium, High, or Urgent")
        ], default="Low")

    return Plan  # Return a reference to the class and not an object!
