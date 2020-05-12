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
    department = Column(String(50), nullable=False, unique=True)


class TitleLookup(db.Model):
    __tablename__ = 'title_lookup'

    id = Column(Integer, primary_key=True)
    title = Column(String(45), nullable=False, unique=True)


class Employee(db.Model):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True)
    employeeID = Column(String(200), nullable=False, unique=True)
    email = Column(VARCHAR(255), nullable=False, unique=True)
    _pass = Column('pass', VARCHAR(128), nullable=False)
    firstname = Column(VARCHAR(45), nullable=False)
    lastname = Column(VARCHAR(45), nullable=False)
    user_dept_FK = Column(ForeignKey('department_lookup.id'), nullable=False, index=True)
    user_title_FK = Column(ForeignKey('title_lookup.id'), nullable=False, index=True)

    department_lookup = relationship('DepartmentLookup')
    title_lookup = relationship('TitleLookup')


db.create_all()
