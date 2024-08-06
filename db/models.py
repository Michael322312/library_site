from sqlalchemy import Boolean, ForeignKey, Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from fastapi.security import OAuth2PasswordBearer
from enum import StrEnum, auto


from db.engine import Base

class DBAuthor(Base):
    __tablename__ = "author"
    
    id = Column(Integer,primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sec_name = Column(String(255), nullable=False)
    img_path = Column(String, nullable="False")


class CoverType(StrEnum):
    HARD = auto()
    SOFT = auto()

class DBBook(Base):
    __tablename__ = "book"

    id = Column(Integer,primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique= True)
    pages = Column(Integer, nullable=False)
    cover_type = Column(Enum(CoverType), nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    img_path = Column(String, nullable="False")
    
    author = relationship(DBAuthor)


class DBUser(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(63), nullable=False, unique=True)
    password = Column(String(63), nullable=False)
    


