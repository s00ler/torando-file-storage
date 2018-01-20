from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Page(Base):
    """Implement inteface to database table with pages."""

    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True)
    origin_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    origin = relationship('File', back_populates='pages')
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
