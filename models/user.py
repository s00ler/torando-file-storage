from sqlalchemy import Column, Integer, String
from .base import Base


class User(Base):
    """Implement inteface to database table with users."""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
