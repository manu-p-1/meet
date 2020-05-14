from server import db
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import VARCHAR
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
    firstname = Column(VARCHAR(45), nullable=False)
    lastname = Column(VARCHAR(45), nullable=False)
    user_dept_FK = Column(ForeignKey('department_lookup.token'), nullable=False, index=True)

    department_lookup = relationship('DepartmentLookup')

db.drop_all()
db.create_all()