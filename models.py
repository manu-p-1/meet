from sys import stderr


class Plan:

    def __init__(self, cursor, conn=None):
        self._cursor = cursor
        self._conn = conn
        self._generic_insert = '''INSERT INTO plan (plan_name,funding_amount,plan_justification,memo,start_date,end_date,
                    source_fund_FK, dest_fund_FK,fund_individuals,control_name, control_window,amount_limit,usage_limit,complete) VALUES 
                    (%s,%s,%s,%s,%s,%s,
                    (SELECT id FROM department_lookup WHERE department = %s),
                    (SELECT id FROM department_lookup WHERE department = %s),
                    %s,%s,%s,%s,%s,%s)'''

        self._generic_select = """SELECT * FROM plan"""

    def insert_with_form(self, form):

        for field in form:
            if field.data == '':
                field.data = None

        self._cursor.execute(self._generic_insert, (form.planName.data, form.fundingAmount.data,
                                                    form.planJustification.data, form.memo.data,
                                                    form.startDate.data,
                                                    form.endDate.data, form.sourceFund.data, form.destFund.data,
                                                    form.fundIndivEmployeesToggle.data,
                                                    form.controlName.data, form.controlWindow.data,
                                                    form.amountLimit.data,
                                                    form.usageLimit.data, False))

        v = """SELECT id FROM `plan` WHERE plan_name = (%s)"""
        self._cursor.execute(v, form.planName.data)
        plid = self._cursor.fetchone()[0]

        print("EMPLOYEES OPTIONAL", form.employeesOptional.data, file=stderr)
        if len(form.employeesOptional.data) != 0 and form.employeesOptional.data[0] != '':
            q = """INSERT INTO `employee_plan`(ep_employee_FK, ep_plan_fk) 
                                  VALUES ( %s,  %s)"""
            for employeeField in form.employeesOptional.data:
                print("EMPLOYEE FIELD", employeeField, file=stderr)
                self._cursor.execute(q, (employeeField.data['id'], plid))

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
            self._conn.close()

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
            self._conn.close()

    def select_all(self):
        self._cursor.execute(self._generic_select)
        return self._cursor.fetchall()[0][0]
