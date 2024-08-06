from pydantic import BaseModel

class AuthorBase(BaseModel):
    name: str
    sec_name: str
    img_path: str


class AuthorCreator(AuthorBase):
    pass

class Author(AuthorBase):
    id: int
    class Config:
        from_attributes = True

class BookBase(BaseModel):
    name: str
    pages: int
    cover_type: str
    img_path: str
    author_id: int


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int
    author_id: int
    img_path: str
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    login: str
    password: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    class Config:
        from_attributes = True
