from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, BooleanField, DecimalField, HiddenField, \
    RadioField, FieldList
from wtforms.validators import InputRequired, NumberRange, Length, AnyOf
from wtforms.widgets.html5 import NumberInput

from modules.routes.user.custom_fields import EmployeeInfoTextAreaField
from modules.routes.user.custom_validators import RequiredIf, EmployeeUnique, EndDateProper, \
    StartDateProper, RequiredIfRadioField, VelocityUsageLimit, DeptBalance
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
        create_plan_btn = InlineSubmitField("Create Plan", btn_text="Create Plan",
                                            render_kw={"class": "btn btn-primary btn-block"})

    return CreatePlanForm()


def get_plan_form(sn: dict):
    """
    GET PLAN FORM
    :param sn: Session Dictionary
    :return: A Manage Plan Form
    """

    class ManagePlanForm(get_plan_base(sn)):
        update_plan_btn = InlineSubmitField("Update Plan", btn_text="Update Plan",
                                            render_kw={"class": "btn btn-primary btn-block"})

    return ManagePlanForm()


def get_plan_base(sn: dict):
    """
    GET REFERENCE TO PLAN BASE FORM
    :param sn: Session Dictionary
    :return: A Plan Form
    """

    class Plan(FlaskForm):
        DISB_ALL = "DISB_ALL"
        DISB_INDIV = "DISB_INDIV"
        MINIMUM_FUND_AMT = 15.00
        MINIMUM_CONTROL_AMT = 1.00

        plan_name = StringField("Plan Name",
                                validators=[
                                    InputRequired(message="Enter a plan name."),
                                    Length(min=2, max=255, message="Plan name was too short or too long")
                                ],
                                render_kw={"placeholder": "Plan Name",
                                           "class": "form-control"})

        funding_amount = DecimalField('Per-Employee Funding Amount',
                                      validators=[
                                          InputRequired(message="Enter a funding amount."),
                                          NumberRange(min=MINIMUM_FUND_AMT,
                                                      message=f"The minimum funding amount must be at "
                                                              f"least ${MINIMUM_FUND_AMT}."),
                                          DeptBalance(client=client, sn=sn)
                                      ],
                                      render_kw={"placeholder": "Funding Amount",
                                                 "class": "form-control"},
                                      widget=NumberInput())

        plan_justification = StringField('Plan Justification (e.g. Travel, Equipment, Party)',
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

        start_date = StringField('Start Date/Times',
                                 validators=[
                                     InputRequired(message="A start date is required."),
                                     StartDateProper()
                                 ],
                                 render_kw={"placeholder": "Start Date/Times",
                                            "class": "form-control"})

        source_fund = SelectField('Fund Source',
                                  validators=[
                                      InputRequired(message="A funding source department is required."),
                                      AnyOf([sn['manager_dept']], message="The funding source department must be"
                                                                          "from your own department")
                                  ],
                                  choices=[
                                      (
                                          sn['manager_dept'],
                                          client.READABLE_DEPARTMENTS[sn['manager_dept']]
                                      )
                                  ],
                                  render_kw={"class": "form-control"})

        dest_fund = SelectField('Fund Destination',
                                validators=[
                                    InputRequired(message="A funding destination department is required."),
                                    AnyOf([x[0] for x in DEPT_MAPPINGS if x[0] != ''],
                                          message="Please select a valid department option")
                                ],
                                choices=DEPT_MAPPINGS,
                                render_kw={"class": "form-control"})

        has_fund_individuals = BooleanField('Employee specific disbursement',
                                            render_kw={"class": "custom-control-input"})

        disbursement_type = RadioField('Employee Disbursement Type', choices=[
            (DISB_ALL, 'Disburse to all Employees'),
            (DISB_INDIV, 'Search for an Employee'),
        ], default=DISB_ALL, validators=[RequiredIf('has_fund_individuals',
                                                    message="To disburse funds, search for an employee or disburse"
                                                            "to all employees")])

        employees_list = FieldList(EmployeeInfoTextAreaField('employees_list',
                                                             validators=[
                                                                 RequiredIfRadioField(
                                                                     'disbursement_type',
                                                                     DISB_INDIV,
                                                                     message="Please specify at "
                                                                             "least 1 employee to "
                                                                             "disburse funds to.")
                                                             ]),
                                   validators=[EmployeeUnique(object_name="employee id's")],
                                   min_entries=1,
                                   max_entries=24)

        has_end_date = BooleanField('Add End Date',
                                    render_kw={"class": "custom-control-input"})

        end_date = StringField('End Date/Times',
                               validators=[
                                   RequiredIf("has_end_date", message="The end date is required."),
                                   EndDateProper(),
                               ],
                               render_kw={"placeholder": "Date Date/Times",
                                          "class": "form-control"})

        has_velocity_controls = BooleanField('Add Velocity Controls',
                                             render_kw={"class": "custom-control-input"})

        vel_control_name = StringField('Control Name (min 3 chars, max 50 chars.)',
                                       validators=[
                                           RequiredIf('has_velocity_controls',
                                                      message="The velocity control, control name is required."),
                                           Length(min=3, max=50)
                                       ],
                                       render_kw={"class": "form-control",
                                                  "placeholder": "Enter a Control Name"})

        vel_control_window = SelectField('Control Window',
                                         validators=[
                                             RequiredIf('has_velocity_controls',
                                                        message="The velocity control, control window is required."),
                                             AnyOf(values=["day", "week", "month", "lifetime", "transaction"],
                                                   message="Please select a valid velocity control window option")
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

        vel_amt_limit = DecimalField('Amount Limit',
                                     validators=[
                                         RequiredIf('has_velocity_controls',
                                                    message="The velocity control amount limit is required."),
                                         NumberRange(min=MINIMUM_CONTROL_AMT,
                                                     message=f"The minimum velocity control amount limit must be at "
                                                             f"least ${MINIMUM_CONTROL_AMT}."),
                                         VelocityUsageLimit()
                                     ],
                                     render_kw={"placeholder": "Amount Limit",
                                                "class": "form-control"},
                                     widget=NumberInput())

        vel_usage_limit = IntegerField('Usage Limit (1 - 100)',
                                       validators=[
                                           RequiredIf('has_velocity_controls',
                                                      message="The velocity control usage limit is required."),
                                           NumberRange(min=1, max=100,
                                                       message="The velocity control usage limit should be between "
                                                               "1 and 100, inclusive.")
                                       ],
                                       render_kw={"placeholder": "Usage Limit",
                                                  "class": "form-control"},
                                       widget=NumberInput())

        time_zone = HiddenField(validators=[InputRequired(message="The timezone is a required field")])

        priority = HiddenField(validators=[
            InputRequired(message="Priority is a required field"),
            AnyOf(values=["Low", "Medium", "High", "Urgent"],
                  message="Please select a priority option")
        ], default="Low")

    return Plan  # Return a reference to the class and not an object!


class Forminator:

    def __init__(self, form):
        # These will always be required
        self._form = form

        self._plan_name: str = form.plan_name.data
        self._funding_amount: str = form.funding_amount.data
        self._plan_justification = form.plan_justification.data
        self._memo = form.memo.data
        self._start_date = form.start_date.data
        self._source_fund = form.source_fund.data
        self._dest_fund = form.dest_fund.data

        # Here on out is optional
        self._has_fund_individuals = form.has_fund_individuals.data
        self._disbursement_type = form.disbursement_type.data

        # We only want the field list here NOT the data
        self._employees_list = form.employees_list

        self._has_end_date = form.has_end_date.data
        self._end_date = form.end_date.data

        self._has_velocity_controls = form.has_velocity_controls.data
        self._vel_control_name = form.vel_control_name.data
        self._vel_control_window = form.vel_control_window.data
        self._vel_amt_limit = form.vel_amt_limit.data
        self._vel_usage_limit = form.vel_usage_limit.data

        self._time_zone = form.time_zone.data
        self._priority = form.priority.data

        self.clean()

    def clean(self):
        self._scrub_plan_name()
        self._scrub_plan_justification()
        self._scrub_memo()
        self._scrub_dates()

        # strings are truthy

        if self._vel_control_name:
            self._scrub_vel_control_name()

    def _scrub_plan_name(self):
        self._plan_name = self.scrub_plan_name(self._plan_name)

    def _scrub_plan_justification(self):
        self._plan_justification = self.scrub_plan_name(self._plan_justification)  # We just use the same filter

    def _scrub_memo(self):
        self._memo = self.scrub_plan_name(self._memo)  # We just use the same filter

    def _scrub_dates(self):
        self._start_date = self.scrub_date(self._start_date)

        if self._end_date:
            self._end_date = self.scrub_date(self._end_date)

    def _scrub_vel_control_name(self):
        self._vel_control_name = self.scrub_plan_name(self._vel_control_name)

    @staticmethod
    def scrub_date(date):
        return date.strip()

    @staticmethod
    def scrub_plan_name(name):
        return " ".join(name.split()).capitalize()

    def is_disbursed_all(self):
        x = self.has_fund_individuals and self.disbursement_type == self._form.DISB_ALL
        if x is None:
            return False
        return x

    def retrieve(self):
        return self

    @property
    def plan_name(self):
        return self._plan_name

    @property
    def funding_amount(self):
        return self._funding_amount

    @property
    def plan_justification(self):
        return self._plan_justification

    @property
    def memo(self):
        return self._memo

    @property
    def start_date(self):
        return self._start_date

    @property
    def source_fund(self):
        return self._source_fund

    @property
    def dest_fund(self):
        return self._dest_fund

    @property
    def has_fund_individuals(self):
        return self._has_fund_individuals

    @property
    def disbursement_type(self):
        return self._disbursement_type if self._disbursement_type else None

    @property
    def employees_list(self):
        e_list = self._employees_list.data
        if len(e_list) != 0 and e_list[0] != '':
            for employeeField in e_list:
                yield employeeField
        else:
            yield []

    @employees_list.setter
    def employees_list(self, e_list):
        self._employees_list.pop_entry()  # Remove the default entry
        [self._employees_list.append_entry(e) for e in e_list]

    @property
    def has_end_date(self):
        return self._has_end_date if self._has_end_date else None

    @property
    def end_date(self):
        return self._end_date if self._end_date else None

    @property
    def has_velocity_controls(self):
        return self._has_velocity_controls if self._has_velocity_controls else None

    @property
    def vel_control_name(self):
        return self._vel_control_name if self._vel_control_name else None

    @property
    def vel_control_window(self):
        return self._vel_control_window if self._vel_control_window else None

    @property
    def vel_amt_limit(self):
        return self._vel_amt_limit if self._vel_amt_limit else None

    @property
    def vel_usage_limit(self):
        return self._vel_usage_limit if self._vel_usage_limit else None

    @property
    def raw_form(self):
        return self._form

    @property
    def time_zone(self):
        return self._time_zone

    @property
    def priority(self):
        return self._priority
