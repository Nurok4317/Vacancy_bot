from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
from db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    is_authorized = Column(Boolean, default=False, nullable=False)
    registered_at = Column(TIMESTAMP, server_default=func.current_timestamp())

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    added_at = Column(TIMESTAMP, server_default=func.current_timestamp())

class UserFilter(Base):
    __tablename__ = 'user_filters'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    keywords = Column(String, default='')
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
