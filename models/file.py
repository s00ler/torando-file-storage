from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class File(Base):
    """Implement inteface to database table with files."""

    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    pages = relationship('Page', back_populates='origin')
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
