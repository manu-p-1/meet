from abc import ABC, abstractmethod
from sys import stderr
from datetime import datetime


class Model(ABC):

    def __init__(self, cursor, conn, generic_insert, generic_select, generic_select_where, immediate_commit):
        self._cursor = cursor
        self._conn = conn
        self._generic_insert = generic_insert
        self._generic_select = generic_select
        self._generic_select_where = generic_select_where
        self._immediate_commit = immediate_commit

    @abstractmethod
    def insert(self, *args):
        pass

    def select_all(self):
        self._cursor.execute(self._generic_select)
        return self._cursor.fetchall()

    def select_where(self, column_name, condition):
        self._cursor.execute(self._generic_select_where, (column_name, condition))
        return self._cursor.fetchall()

    def close_connection(self):
        self._conn.close()

    @property
    def get_conn(self):
        return self._conn

    @property
    def get_cursor(self):
        return self._cursor

    @property
    def is_immediate_commit(self):
        return self._immediate_commit


class Plan(Model):

    def __init__(self, cursor, conn, immediate_commit=True):

        insert = '''INSERT INTO plan (plan_name,funding_amount,plan_justification,memo,start_date,end_date,
                    source_fund_FK, dest_fund_FK,fund_individuals,control_name, control_window,amount_limit,usage_limit,complete) VALUES 
                    (%s,%s,%s,%s,%s,%s,
                    (SELECT id FROM department_lookup WHERE department = %s),
                    (SELECT id FROM department_lookup WHERE department = %s),
                    %s,%s,%s,%s,%s,%s)'''
        select = """SELECT * FROM plan"""
        select_where = "SELECT * FROM plan WHERE %s = %s"

        super().__init__(cursor, conn, insert, select, select_where, immediate_commit)

    def insert(self, form):

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

        if len(form.employeesOptional.data) != 0 and form.employeesOptional.data[0] != '':
                for employeeField in form.employeesOptional.data:
                    ep = EmployeePlan(self.get_cursor, self.get_conn, True)
                    ep.insert_with_id(employeeField['id'],form.planName.data)

        if self.is_immediate_commit:
            self._conn.commit()

    def update(self,form,plan_id):
        for field in form:
            if field.data == '':
                field.data = None

        update_query = '''UPDATE plan SET plan_name = %s,plan_justification = %s,memo = %s,end_date = %s,
                    fund_individuals = %s,control_name = %s, control_window = %s,amount_limit = %s,usage_limit = %s
                    WHERE id = %s'''
        self._cursor.execute(update_query, (form.planName.data,
                                            form.planJustification.data, form.memo.data,
                                            form.endDate.data,
                                            form.fundIndivEmployeesToggle.data,
                                            form.controlName.data, form.controlWindow.data,
                                            form.amountLimit.data,
                                            form.usageLimit.data, plan_id))
        if self.is_immediate_commit:
            self._conn.commit()


class Manager(Model):

    def __init__(self, cursor, conn, immediate_commit=True):
        insert = '''INSERT INTO manager(email, pass, first_name, last_name, title, description, manager_dept_FK) VALUES 
                    (%s,%s,%s,%s,%s,%s,%s)'''
        select = """SELECT * FROM manager"""
        select_where = """SELECT * FROM manager where %s = %s"""

        super().__init__(cursor, conn, insert, select, select_where, immediate_commit)

    def insert(self, email, pass_, first_name, last_name, title, description, manager_dept_FK, loop=False):
        self._cursor.execute(self._generic_insert,
                             (email, pass_, first_name, last_name, title, description, manager_dept_FK))

        if self.is_immediate_commit:
            self._conn.commit()


class Employee(Model):

    def __init__(self, cursor, conn, immediate_commit=True):
        insert = '''INSERT INTO employee(token, first_name, last_name, employee_dept_FK) VALUES (%s,%s,%s,%s)'''
        select = """SELECT * FROM employee"""
        select_where = """SELECT * FROM employee where %s = %s"""

        super().__init__(cursor, conn, insert, select, select_where, immediate_commit)

    def insert(self, token, first_name, last_name, employee_dept_FK):
        self._cursor.execute(self._generic_insert, (token, first_name, last_name, employee_dept_FK))

        if self.is_immediate_commit:
            self._conn.commit()


class Transaction(Model):

    def __init__(self, cursor, conn, immediate_commit=True):
        insert = '''INSERT INTO transaction(src_token, dest_token, create_time, amount, src_token_is_card) 
        VALUES (%s, %s, %s, %s, %s)'''
        select = """SELECT * FROM transaction"""
        select_where = """SELECT * FROM transaction WHERE %s = %s"""

        super().__init__(cursor, conn, insert, select, select_where, immediate_commit)

    def insert(self, src_token, dest_token, create_time, amount, is_card=False):
        self._cursor.execute(self._generic_insert, (src_token, dest_token, create_time, amount, is_card))

        if self.is_immediate_commit:
            self._conn.commit()

    @classmethod
    def current_time(cls, transaction_time):
        return datetime.strptime(transaction_time, "%Y-%m-%dT%H:%M:%SZ")


class EmployeeCard(Model):

    def __init__(self, cursor, conn, immediate_commit=True):
        insert = '''INSERT INTO employee_card(ec_employee_token, ec_card_token) 
        VALUES (%s, %s)'''
        select = """SELECT * FROM employee_card"""
        select_where = """SELECT * FROM employee_card WHERE %s = %s"""

        super().__init__(cursor, conn, insert, select, select_where, immediate_commit)

    def insert(self, employee_token, card_token):
        self._cursor.execute(self._generic_insert, (employee_token, card_token))

        if self.is_immediate_commit:
            self._conn.commit()


class EmployeePlan(Model):

    def __init__(self, cursor, conn, immediate_commit=True):
        insert = '''INSERT INTO employee_plan(ep_employee_FK, ep_plan_fk, ep_card_token) 
        VALUES (
        (SELECT id FROM employee WHERE token = %s), 
        (SELECT id FROM plan WHERE plan_name = %s),
        %s
        )'''
        select = """SELECT * FROM employee_plan"""
        select_where = """SELECT * FROM employee_plan WHERE %s = %s"""

        super().__init__(cursor, conn, insert, select, select_where, immediate_commit)

    def insert(self, employee_token, plan_name, card_token=None):
        self._cursor.execute(self._generic_insert, (employee_token, plan_name, card_token))

        if self.is_immediate_commit:
            self._conn.commit()

    def insert_with_id(self, employee_id, plan_name, card_token=None):
        
        insert = '''INSERT INTO employee_plan(ep_employee_FK, ep_plan_fk, ep_card_token) 
                    VALUES (
                    (SELECT id FROM employee WHERE id = %s), 
                    (SELECT id FROM plan WHERE plan_name = %s),
                    %s)'''
        self._cursor.execute(insert, (employee_id, plan_name, card_token))

        if self.is_immediate_commit:
            self._conn.commit()
