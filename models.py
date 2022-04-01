#!/usr/bin/env python3
from sqlalchemy import create_engine, Column
from sqlalchemy.types import Integer, String, Date, DateTime, JSON, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('mysql+pymysql://root:$Sylvain1234@localhost/tifolive', echo=True)
Base = declarative_base()


class Stadium(Base):
    __tablename__ = 'stadiums'
    id = Column(Integer, primary_key=True)
    short = Column(String(20), unique=True)
    name = Column(String(50))
    capacity = Column(Integer)
    address = Column(String(50))

    seats = relationship("Seat", backref="stadiums")

    def __repr__(self):
        return "<Stadium(short='%s')>" % (self.short)


class Seat(Base):
    __tablename__ = 'seats'
    id = Column(Integer, primary_key=True)
    short = Column(String(1))
    name = Column(String(20))
    partition = Column(JSON)
    stadium_id = Column(Integer, ForeignKey('stadiums.id'))

    def __repr__(self):
        return "<Seat(short='%s')>" % (self.short)


seats_table = Seat.__table__
stadiums_table = Stadium.__table__
metadata = Base.metadata


def create_all():
    metadata.create_all(engine)
