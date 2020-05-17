import sys

from server import db
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.dialects.mysql import VARCHAR, DATETIME, BOOLEAN, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

db.metadata.clear()
db.session.commit()
print(db.metadata, file=sys.stderr)
for tbl in reversed(metadata.sorted_tables):
    db.execute(tbl.delete())
    db.session.commit()


class DepartmentLookup(db.Model):
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    token = Column(String(200), nullable=False, unique=True)
    department = Column(String(50), nullable=False, unique=True)


class Manager(db.Model):
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    email = Column(VARCHAR(255), nullable=False, unique=True)
    _pass = Column('pass', VARCHAR(128), nullable=False)
    first_name = Column(VARCHAR(45), nullable=False)
    last_name = Column(VARCHAR(45), nullable=False)
    title = Column(VARCHAR(50), nullable=False)
    description = Column(VARCHAR(500), nullable=True)
    manager_dept_FK = Column(ForeignKey(
        'department_lookup.id'), nullable=False, index=True)

    def check_password(self, password):
        if self._pass == password:
            return True
        return False


class Employee(db.Model):
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    token = Column(String(200), nullable=False, unique=True)
    first_name = Column(VARCHAR(45), nullable=False)
    last_name = Column(VARCHAR(45), nullable=False)
    user_dept_FK = Column(ForeignKey(
        'department_lookup.token'), nullable=False, index=True)


class Plan(db.Model):
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=1)
    plan_name = Column(String(200), nullable=False, unique=True)
    funding_amount = Column(DECIMAL(12, 2), nullable=False)
    plan_justification = Column(VARCHAR(300), nullable=False)
    description = Column(VARCHAR(300), nullable=False)
    start_date = Column(DATETIME, nullable=False)
    end_date = Column(DATETIME, nullable=False)
    source_fund = Column(ForeignKey('department_lookup.id'), nullable=False)
    dest_fund = Column(ForeignKey('department_lookup.id'), nullable=False)
    fund_individuals = Column(BOOLEAN, nullable=False)
    control_name = Column(VARCHAR(50))
    control_window = Column(DATETIME)
    amount_limit = Column(DECIMAL(12, 2))
    usage_limit = Column(Integer)
    complete = Column(BOOLEAN, nullable=False)


class UserPlan(db.Model):
    __table_args__ = {'extend_existing': True}

    user_FK = Column(ForeignKey('employee.id'),
                     primary_key=True, nullable=False)
    plan_FK = Column(ForeignKey('plan.id'), primary_key=True, nullable=False)


db.drop_all()
db.session.commit()

db.create_all()
