from modules.routes.user.forms import CreatePlanForm


class Plan:

    def __init__(self, cursor, conn=None):
        self._cursor = cursor
        self._conn = conn
        self._generic_insert = '''INSERT INTO plan (plan_name,funding_amount,plan_justification,memo,start_date,end_date,
                    source_fund_FK,dest_fund_FK,fund_individuals,control_name, control_window,amount_limit,usage_limit,complete) VALUES 
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

        self._generic_select = """SELECT * FROM plan"""

    def insert_with_form(self, form):
        if form is not None:
            self._cursor.execute(self._generic_insert, (form.planName.data, form.fundingAmount.data,
                                                        form.planJustification.data, form.memo.data,
                                                        form.startDate.data,
                                                        form.endDate.data, form.sourceFund.data, form.destFund.data,
                                                        form.fundIndivEmployeesToggle.data,
                                                        form.controlName.data, form.controlWindow.data,
                                                        form.amountLimit.data,
                                                        form.usageLimit.data, False))
            if self._conn is not None:
                self._conn.commit()

    def insert_without_form(self, plane_name, funding_amount, plan_justification, description, start_date, end_date,
                            source_fund, dest_fund, fund_individuals, control_name, control_window, amount_limit,
                            usage_limit, complete):
        self._cursor.execute(self._generic_insert, (plane_name, funding_amount,
                                                    plan_justification.data, description, start_date,
                                                    end_date, source_fund, dest_fund,
                                                    fund_individuals,
                                                    control_name, control_window,
                                                    amount_limit,
                                                    usage_limit, complete))
        if self._conn is not None:
            self._conn.commit()

    def select_all(self):
        self._cursor.execute(self._generic_select)
        return self._cursor.fetchall()[0][0]


class Manager:

    def __init__(self, cursor, conn=None):
        self._cursor = cursor
        self._conn = conn
        self._generic_insert = '''
        INSERT INTO manager(email, pass, first_name, last_name, title, description, manager_dept_FK) VALUES 
                    (%s,%s,%s,%s,%s,%s,%s)'''

        self._generic_select = """SELECT * FROM manager"""

    def insert(self, email, pass_, first_name, last_name, title, description, manager_dept_FK):
        self._cursor.execute(self._generic_insert,
                             (email, pass_, first_name, last_name, title, description, manager_dept_FK))

        if self._conn is not None:
            self._conn.commit()

    def select_all(self):
        self._cursor.execute(self._generic_select)
        return self._cursor.fetchall()[0][0]


class Employee:

    def __init__(self, cursor, conn=None):
        self._cursor = cursor
        self._conn = conn
        self._generic_insert = '''
        INSERT INTO employee(token, first_name, last_name, employee_dept_FK) VALUES 
                    (%s,%s,%s,%s)'''

        self._generic_select = """SELECT * FROM employee"""

    def insert(self, token, first_name, last_name, employee_dept_FK):
        self._cursor.execute(self._generic_insert, (token, first_name, last_name, employee_dept_FK))

        if self._conn is not None:
            self._conn.commit()

    def select_all(self):
        self._cursor.execute(self._generic_select)
        return self._cursor.fetchall()[0][0]
