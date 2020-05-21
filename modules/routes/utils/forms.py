from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, BooleanField, SubmitField, DecimalField, \
    FieldList
from wtforms.validators import InputRequired, NumberRange, Length
from wtforms.widgets.html5 import NumberInput

from modules.routes.user.custom_fields import EmployeeInfoTextAreaField
from modules.routes.user.custom_validators import RequiredIf, DateProper, EmployeeUnique

from server import client


def get_plan_form(plan: dict,sn:dict, fund_choices: list):
    if plan['fund_individuals'] == 1:
        plan['fund_individuals'] = True
    if plan['end_date'] != '':
        plan['end_date_toggle'] = True
    if plan['control_name'] != '':
        plan['control_toggle'] = False
    
    class ManagePlanForm(FlaskForm):
        planName = StringField("Plan Name", validators=[InputRequired(message="Enter a plan name.")],
                               render_kw={"placeholder": "Plan Name",
                                          "class": "form-control",
                                          "value":plan['plan_name']})

        fundingAmount = DecimalField('Funding Amount',
                                     validators=[
                                         InputRequired(message="Enter a funding amount."),
                                         NumberRange(min=100.00,
                                                     message="The minimum funding amount must be at least $100.00.")
                                     ],
                                     render_kw={"placeholder": "Funding Amount",
                                                "class": "form-control",
                                                "disabled":"",
                                                "value":plan['funding_amount']},
                                     widget=NumberInput())

        planJustification = StringField('Plan Justification (e.g. Travel, Equipment, Party)',
                                        validators=[
                                            InputRequired(message="A plan justification is required."),
                                            Length(min=3, max=50,
                                                   message="Plan justification was either too short or too long.")
                                        ],
                                        render_kw={"placeholder": "Plan Justification",
                                                   "class": "form-control",
                                                   "value":plan['plan_justification']})

        memo = TextAreaField('Memo (min 10 chars, max 255 chars.)',
                             validators=[
                                 InputRequired("A memo is required."),
                                 Length(min=10, max=255, message="Memo was either too short or too long.")
                             ],
                             render_kw={"rows": 4,
                                        "maxlength": 255,
                                        "placeholder": "Memo Description",
                                        "class": "form-control",
                                        "value":plan['memo']})

        destFund = SelectField('Fund Destination',
                           validators=[InputRequired(message="A funding destination department is required.")],
                           choices=[
                                ('', 'Destination Fund Department'),
                                ('IT', "Information Technology"),
                                ('AC', "Accounting"),
                                ('MK',"Marketing"),
                                ('HR', "Human Resources"),
                                ('PD',"Project Development"),
                                ('RD', "Research and Development"),
                                ('SC',"Some Stuff Dont Know"),
                                ('LG','Legal')
                           ],
                           render_kw={"class": "form-control",
                           "disabled":"",
                           "value":plan['dest_fund_FK']},
                           default='')

        fundIndivEmployeesToggle = BooleanField('Employee specific disbursement', default=plan['fund_individuals'],
                                            render_kw={"class": "custom-control-input",
                                            "disabled":""})

        employeesOptional = FieldList(EmployeeInfoTextAreaField('employeesOptional',
                                                            validators=[
                                                                RequiredIf('fundIndivEmployeesToggle',
                                                                           message="Please specify at least 1 "
                                                                                   "employee to disburse funds to."),
                                                            ]),
                                  validators=[EmployeeUnique(object_name="employee id's")],
                                  min_entries=1,
                                  max_entries=12)

        endDateToggle = BooleanField('Add End Date', default=plan['end_date_toggle'], render_kw={"class": "custom-control-input"})

        endDate = StringField('End Date/Times',
                          validators=[
                              RequiredIf("endDateToggle", message="The end date is required."),
                              DateProper(message="The end date is malformed.")
                          ],
                          render_kw={"placeholder": "Date Date/Times",
                                     "class": "form-control"})

        controlToggle = BooleanField('Add Velocity Controls', default=plan['control_toggle'],
                                 render_kw={"class": "custom-control-input"})

        controlName = StringField('Control Name',
                              validators=[
                                  RequiredIf('controlToggle',
                                             message="The velocity control, control name is required."),
                                  Length(max=50)
                              ],
                              render_kw={"class": "form-control",
                                         "placeholder": "Enter a Control Name",
                                         "value":plan['control_name']})

        startDate = StringField('Start Date/Times',
                                validators=[
                                    InputRequired(message="A start date is required."),
                                    DateProper(message="The start date is malformed.")
                                ],
                                render_kw={"placeholder": "Start Date/Times",
                                           "class": "form-control",
                                           "disabled":"",
                                           "value":plan['start_date']})

        sourceFund = SelectField('Fund Source',
                                 validators=[InputRequired(message="A funding source department is required.")],
                                 choices=[
                                     (
                                         sn['manager_dept'],
                                         [x for x in client.DEPT_MAPPINGS if x[0] == sn['manager_dept']][0][1]
                                     )
                                 ],
                                 render_kw={"class": "form-control",
                                 "disabled":"",
                                 "value":sn['manager_dept']},
                                 default='')

        destFund = SelectField('Fund Destination',
                               validators=[InputRequired(message="A funding destination department is required.")],
                               choices=fund_choices,
                               render_kw={"class": "form-control",
                               "disabled":"",
                               "value":plan['dest_fund_FK']},
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

        endDateToggle = BooleanField('Add End Date', default=plan['end_date_toggle'], render_kw={"class": "custom-control-input","disabled":""})

        endDate = StringField('End Date/Times',
                              validators=[
                                  RequiredIf("endDateToggle", message="The end date is required."),
                                  DateProper(message="The end date is malformed.")
                              ],
                              render_kw={"placeholder": "Date Date/Times",
                                         "class": "form-control",
                                         "value":plan['end_date']})

        controlToggle = BooleanField('Add Velocity Controls', default=False,
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
                                    render_kw={"class": "form-control"},
                                    default=plan['control_window'])

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
                                              "value":plan['amount_limit']},
                                   widget=NumberInput())

        usageLimit = IntegerField('Usage Limit',
                                  validators=[
                                      RequiredIf('controlToggle',
                                                 message="The velocity control usage limit is required."),
                                      NumberRange(min=0, max=100,
                                                  message="The velocity control usage limit should be between 0 and 100, "
                                                          "inclusive.")
                                  ],
                                  render_kw={"placeholder": "Usage Limit",
                                             "class": "form-control",
                                             "value":plan['usage_limit']},
                                  widget=NumberInput())

        updatePlanButton = SubmitField("Update Plan", render_kw={"class": "btn btn-primary btn-block"})

    return ManagePlanForm()

def get_empty_manage_form(sn,fund_choices):
    class EmptyManageForm(FlaskForm):
        planName = StringField("Plan Name", validators=[InputRequired(message="Enter a plan name.")],
                               render_kw={"placeholder": "Plan Name",
                                          "class": "form-control",
                                          "disabled":""})

        fundingAmount = DecimalField('Funding Amount',
                                     validators=[
                                         InputRequired(message="Enter a funding amount."),
                                         NumberRange(min=100.00,
                                                     message="The minimum funding amount must be at least $100.00.")
                                     ],
                                     render_kw={"placeholder": "Funding Amount",
                                                "class": "form-control",
                                                "disabled":"",
                                                },
                                     widget=NumberInput())

        planJustification = StringField('Plan Justification (e.g. Travel, Equipment, Party)',
                                        validators=[
                                            InputRequired(message="A plan justification is required."),
                                            Length(min=3, max=50,
                                                   message="Plan justification was either too short or too long.")
                                        ],
                                        render_kw={"placeholder": "Plan Justification",
                                                   "class": "form-control",
                                                   "disabled":""})

        memo = TextAreaField('Memo (min 10 chars, max 255 chars.)',
                             validators=[
                                 InputRequired("A memo is required."),
                                 Length(min=10, max=255, message="Memo was either too short or too long.")
                             ],
                             render_kw={"rows": 4,
                                        "maxlength": 255,
                                        "placeholder": "Memo Description",
                                        "class": "form-control",
                                        "disabled":""})

        destFund = SelectField('Fund Destination',
                           validators=[InputRequired(message="A funding destination department is required.")],
                           choices=[
                                ('', 'Destination Fund Department'),
                                ('IT', "Information Technology"),
                                ('AC', "Accounting"),
                                ('MK',"Marketing"),
                                ('HR', "Human Resources"),
                                ('PD',"Project Development"),
                                ('RD', "Research and Development"),
                                ('SC',"Some Stuff Dont Know"),
                                ('LG','Legal')
                           ],
                           render_kw={"class": "form-control",
                           "disabled":"",
                           },
                           default='')

        fundIndivEmployeesToggle = BooleanField('Employee specific disbursement', default=False,
                                            render_kw={"class": "custom-control-input",
                                            "disabled":""})

        employeesOptional = FieldList(EmployeeInfoTextAreaField('employeesOptional',
                                                            validators=[
                                                                RequiredIf('fundIndivEmployeesToggle',
                                                                           message="Please specify at least 1 "
                                                                                   "employee to disburse funds to."),
                                                            ]),
                                  validators=[EmployeeUnique(object_name="employee id's")],
                                  min_entries=1,
                                  max_entries=12)

        endDateToggle = BooleanField('Add End Date', default=False, render_kw={"class": "custom-control-input","disabled":""})

        endDate = StringField('End Date/Times',
                          validators=[
                              RequiredIf("endDateToggle", message="The end date is required."),
                              DateProper(message="The end date is malformed.")
                          ],
                          render_kw={"placeholder": "Date Date/Times",
                                     "class": "form-control",
                                     "disabled":""})

        controlToggle = BooleanField('Add Velocity Controls', default=False,
                                 render_kw={"class": "custom-control-input","disabled":""})

        controlName = StringField('Control Name',
                              validators=[
                                  RequiredIf('controlToggle',
                                             message="The velocity control, control name is required."),
                                  Length(max=50)
                              ],
                              render_kw={"class": "form-control",
                                         "placeholder": "Enter a Control Name",
                                         "disabled":""})

        startDate = StringField('Start Date/Times',
                                validators=[
                                    InputRequired(message="A start date is required."),
                                    DateProper(message="The start date is malformed.")
                                ],
                                render_kw={"placeholder": "Start Date/Times",
                                           "class": "form-control",
                                           "disabled":"",
                                           })

        sourceFund = SelectField('Fund Source',
                                 validators=[InputRequired(message="A funding source department is required.")],
                                 choices=[
                                     (
                                         sn['manager_dept'],
                                         [x for x in client.DEPT_MAPPINGS if x[0] == sn['manager_dept']][0][1]
                                     )
                                 ],
                                 render_kw={"class": "form-control",
                                 "disabled":"",
                                 "value":sn['manager_dept']},
                                 default='')

        destFund = SelectField('Fund Destination',
                               validators=[InputRequired(message="A funding destination department is required.")],
                               choices=fund_choices,
                               render_kw={"class": "form-control",
                               "disabled":"",
                               },
                               default='')

        fundIndivEmployeesToggle = BooleanField('Employee specific disbursement', default=False,
                                                render_kw={"class": "custom-control-input","disabled":""})

        employeesOptional = FieldList(EmployeeInfoTextAreaField('employeesOptional',
                                                                validators=[
                                                                    RequiredIf('fundIndivEmployeesToggle',
                                                                               message="Please specify at least 1 "
                                                                                       "employee to disburse funds to."),
                                                                ]),
                                      validators=[EmployeeUnique(object_name="employee id's")],
                                      min_entries=1,
                                      max_entries=12)

        endDateToggle = BooleanField('Add End Date', default='', render_kw={"class": "custom-control-input","disabled":""})

        endDate = StringField('End Date/Times',
                              validators=[
                                  RequiredIf("endDateToggle", message="The end date is required."),
                                  DateProper(message="The end date is malformed.")
                              ],
                              render_kw={"placeholder": "Date Date/Times",
                                         "class": "form-control",
                                         "disabled":""})

        controlToggle = BooleanField('Add Velocity Controls', default=False,
                                     render_kw={"class": "custom-control-input"})

        controlName = StringField('Control Name',
                                  validators=[
                                      RequiredIf('controlToggle',
                                                 message="The velocity control, control name is required."),
                                      Length(max=50)
                                  ],
                                  render_kw={"class": "form-control",
                                             "placeholder": "Enter a Control Name",
                                             "disabled":""})

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
                                    render_kw={"class": "form-control","disabled":""},
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
                                              "disabled":""},
                                   widget=NumberInput())

        usageLimit = IntegerField('Usage Limit',
                                  validators=[
                                      RequiredIf('controlToggle',
                                                 message="The velocity control usage limit is required."),
                                      NumberRange(min=0, max=100,
                                                  message="The velocity control usage limit should be between 0 and 100, "
                                                          "inclusive.")
                                  ],
                                  render_kw={"placeholder": "Usage Limit",
                                             "class": "form-control",
                                             "disabled":""},
                                  widget=NumberInput())

        updatePlanButton = SubmitField("Update Plan", render_kw={"class": "btn btn-primary btn-block","disabled":""})

    return EmptyManageForm()
