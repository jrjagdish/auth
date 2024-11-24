from sqlalchemy import create_engine, Column, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todos.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    todos = relationship("Todo", back_populates="user")

class Todo(Base):
    __tablename__ = "todos"

    id = Column(String, primary_key=True, index=True)
    text = Column(String, index=True)
    completed = Column(Boolean, default=False)  # Default value for completed
    user_id = Column(String, ForeignKey("users.id"))

    user = relationship("User", back_populates="todos")



    