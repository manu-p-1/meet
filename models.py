from server import db
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.dialects.mysql import VARCHAR,DATETIME, BOOLEAN
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class DepartmentLookup(db.Model):
    __tablename__ = 'department_lookup'

    id = Column(Integer, primary_key=True)
    token = Column(String(200),nullable=False,unique=True)
    department = Column(String(50), nullable=False, unique=True)


class Manager(db.Model):
    __tablename__ = 'manager'

    id = Column(Integer, primary_key=True)
    email = Column(VARCHAR(255), nullable=False, unique=True)
    _pass = Column('pass', VARCHAR(128), nullable=False)

    def check_password(self,password):
        if self._pass == password:
            return True
        return False

class Employee(db.Model):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True)
    token = Column(String(200), nullable=False, unique=True)
    first_name = Column(VARCHAR(45), nullable=False)
    last_name = Column(VARCHAR(45), nullable=False)
    user_dept_FK = Column(ForeignKey('department_lookup.token'), nullable=False, index=True)

    department_lookup = relationship('DepartmentLookup')

class Plan(db.Model):
    __tablename__ = 'plan'

    id = Column(Integer, primary_key=True)
    plan_name = Column(String(200), nullable=False,unique=True)
    funding_amount = Column(Float,nullable=False)
    plan_justification = Column(VARCHAR(300),nullable=False)
    description = Column(VARCHAR(300),nullable=False)
    date_range = Column(DATETIME,nullable=False)
    source_fund = Column(String(50),nullable=False)
    dest_fund = Column(String(50),nullable=False)
    fund_individuals = Column(BOOLEAN,nullable=False)
    control_name = Column(VARCHAR(50))
    control_window = Column(DATETIME)
    amount_limit = Column(Float)
    usage_limit = Column(Integer)

class UserPlan(db.Model):
    __tablename__ = 'user_plan'

    up_plan_FK = Column(ForeignKey('user.id'),nullable=False,index=True)
    up_user_FK = Column(ForeignKey('plan.id'),nullable=False,index=True)

    user = relationship('Employee')
    plan = relationship('Plan')




db.drop_all()
db.create_all()