from fastapi import FastAPI, Depends, HTTPException, status
from auth import (
    OAuth2PasswordRequestForm, verify_password, get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user
)
from datetime import timedelta
from database import engine, Base, SessionLocal, User, Todo
from schemas import TodoCreate, TodoOut, Token, UserCreate
import uuid

# FastAPI app
app = FastAPI()

# Database Initialization
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# Routes
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        db.close()

@app.post("/register")
def register(user: UserCreate):
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already registered")
        
        hashed_password = get_password_hash(user.password)
        new_user = User(id=str(uuid.uuid4()), username=user.username, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        return {"msg": "User registered successfully"}
    finally:
        db.close()

@app.post("/todos/", response_model=TodoOut)
def create_todo(todo: TodoCreate, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        new_todo = Todo(id=str(uuid.uuid4()), text=todo.text, user_id=current_user.id)
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        return new_todo
    finally:
        db.close()

@app.get("/todos/", response_model=list[TodoOut])
def read_todos(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        return db.query(Todo).filter(Todo.user_id == current_user.id).all()
    finally:
        db.close()

@app.put("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: str, todo: TodoCreate, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        existing_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).first()
        if not existing_todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        existing_todo.text = todo.text
        db.commit()
        db.refresh(existing_todo)
        return existing_todo
    finally:
        db.close()

@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: str, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        result = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).delete()
        db.commit()
        if result == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"msg": "Todo deleted successfully"}
    finally:
        db.close()

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
