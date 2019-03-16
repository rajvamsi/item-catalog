import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
            'picture': self.picture
            }


class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return{
            'name': self.name,
            'id': self.id
            }


class Processor(Base):
    __tablename__ = 'processor'
    processor_name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    about = Column(String(250))
    Speciality = Column(String(100))
    cores = Column(Integer)
    threads = Column(Integer)
    cache = Column(String(10))
    processor_id = Column(Integer, ForeignKey('company.id'))
    company = relationship(Company)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return{
            'processor_name': self.processor_name,
            'about': self.about,
            'id': self.id,
            'Speciality': self.Speciality,
            'cores': self.cores,
            'threads': self.threads,
            'cache': self.cache,
            'processor_id': self.processor_id
            }
engine = create_engine('sqlite:///companydata.db')
Base.metadata.create_all(engine)
