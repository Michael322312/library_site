from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException, File
from passlib.context import CryptContext
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_author_books(db: Session, author_id: int):
    return db.query(models.DBBook).filter(models.DBBook.author_id == author_id).all()

def get_author(db: Session, author_id: int):
    return db.query(models.DBAuthor).filter(models.DBAuthor.id == author_id).first()

def get_authors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DBAuthor).offset(skip).limit(limit).all()

def create_author(db: Session, name:str, sec_name:str, img, content):
    path = f'static/authors/{img.filename}'
    with open(path, 'wb') as image:
        image.write(content)

    db_author = models.DBAuthor(
    name=name,
    sec_name = sec_name, img_path = path)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.DBUser(
    login= user.login,
    password = pwd_context.hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_book(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DBBook).offset(skip).limit(limit).all()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DBUser).offset(skip).limit(limit).all()

def get_user(db: Session, name: str):
    return db.query(models.DBUser).filter(models.DBUser.login == name).first()

def get_book_id(db: Session, book_id: int):
    return db.query(models.DBBook).filter(models.DBBook.id == book_id).first()


def create_author_book(db: Session, name, pages, author_id, cover_type, img, content):
    path = f'static/images/{img.filename}'
    with open(path, 'wb') as image:
        image.write(content)
    
    db_book = models.DBBook(name=name, pages=pages, cover_type=cover_type, author_id=author_id, img_path = path)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int):
    db_book = db.query(models.DBBook).filter(models.DBBook.id == book_id).first()
    db.delete(db_book)
    db.commit()

def edit_book(db: Session, book_id: int, new_name: str, pages: int, author_id: int, cover_type: str, file, content):
    b_book = db.query(models.DBBook).filter(models.DBBook.id == book_id).first()
    os.remove(b_book.img_path)
    path = f'static/images/{file.filename}'
    with open(path, 'wb') as image:
        image.write(content)
    b_book.img_path = path
    b_book.author_id = author_id
    b_book.pages = pages
    b_book.name = new_name
    b_book.cover_type = cover_type
    db.commit()
    db.refresh(b_book)
    return b_book
