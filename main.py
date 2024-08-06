
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.engine import sesion_local, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
import sqlite3
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta


SECRET_KEY = "19109197bd5e7c289b92b2b355083ea26c71dee2085ceccc19308a7291b2ea06"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

template = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Залежність
def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

def token_create(data: dict):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

username = "Admin"
password = "adminpass"

conect = sqlite3.connect('library.db')

@app.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    return {'message': 'This data is only for authorizated user'}


@app.post("/author/")
def create_author(name:str, sec_name:str, db: Session = Depends(get_db), img: UploadFile = File(...)):
    return crud.create_author(db=db, name=name, sec_name=sec_name, img=img, content=img.file.read())

@app.post("/user/")
def sign_up(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db,user)


@app.post("/authors/book/")
def create_authors_book(name: str, pages: int, author_id: int, cover_type: str, db: Session = Depends(get_db), current_user: str = Depends(protected), file: UploadFile = File(...)):
    if author_id not in [i.id for i in crud.get_authors(db)]:
        return HTTPException(status_code=404, detail=f"Author with {author_id} not found")
    elif cover_type not in ['HARD', 'SOFT']:
        return HTTPException(status_code=404, detail='Cover type not avaiable! Possible values: HARD, SOFT')
    elif name in [book.name for book in crud.get_book(db)] and author_id in [book.author_id for book in crud.get_book(db)]:
        return HTTPException(status_code=404, detail='Book name has already used Choose another one!')
    else:
        content = file.file.read()
        return crud.create_author_book(db, name, pages, author_id, cover_type, file, content)


@app.get("/authors/", response_model=list[schemas.Author])
def read_authors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    departments = crud.get_authors(db, skip=skip, limit=limit)
    return departments


@app.get("/{author}/books/")
def read_authors_books(author: int, db: Session = Depends(get_db)):
    if author not in [author.id for author in crud.get_authors(db)]:
        return HTTPException(status_code=404, detail=f"Author with {author} not found")
    else:
        return crud.get_author_books(db, author)


@app.get("/")
def read_books(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = crud.get_book(db, skip=skip, limit=limit)
    return template.TemplateResponse('main.html', {'request': request, 'books': books})


@app.get("/books/{book_id}")
def read_books_by_id(request: Request, book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book_id(db, book_id)
    return template.TemplateResponse('book.html', {'request': request, 'book': book, 'author': crud.get_author(db, book.author_id)})


@app.put("/{book_id}/edit")
def edit_book(book_id: int, new_name: str, pages: int, author_id: int, cover_type: str, db: Session = Depends(get_db), current_user: str = Depends(protected), file: UploadFile = File(...)):
    if author_id not in [i.id for i in crud.get_authors(db)]:
        return HTTPException(status_code=404, detail=f"Author with {author_id} not found")
    elif cover_type not in ['HARD', 'SOFT']:
        return HTTPException(status_code=404, detail='Cover type not avaiable! Possible values: HARD, SOFT')
    elif book_id not in [book.id for book in crud.get_book(db)]:
        return HTTPException(status_code=404, detail="Book id not found")
    return crud.edit_book(db, book_id, new_name, pages, author_id, cover_type, file, file.file.read())


@app.delete("/{book_id}/delete")
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: str = Depends(protected)):
    if book_id in [book.id for book in crud.get_book(db)]:
        crud.delete_book(db, book_id)
    else:
        return HTTPException(status_code=404, detail="Book not found")
    

@app.post("/token")
async def token_get(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user_data = crud.get_user(db, form_data.username)
    if not user_data:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    else:
        global user
        user = user_data
        # Перевірка хешів паролів на ідентичність
        if not pwd_context.verify(form_data.password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect username or password") # Аутентифікація пройдена - створюємо токен
        token = token_create(data={"sub": user.login})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/files/")
async def create_file(file: UploadFile = File(...)):
    return {"file_size": file.filename}