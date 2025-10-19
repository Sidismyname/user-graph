from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import uuid4
from models import User, SessionLocal, init_db
from sqlalchemy.orm import Session

init_db()

app = FastAPI()

class UserIn(BaseModel):
    username: str
    age: int
    hobbies: List[str]
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calc_popularity(user: User):
    friends = user.friends
    user_hobbies = set(user.hobbies.split(","))
    shared = 0
    for f in friends:
        shared += len(user_hobbies & set(f.hobbies.split(",")))
    return len(friends) + (shared * 0.5)

@app.get("/")
def home():
    return {"message": "Hello World"}

@app.post("/api/users")
def create_user(data: UserIn):
    db: Session = next(get_db())
    new_user = User(
        id=str(uuid4()),
        username=data.username,
        age=data.age,
        hobbies=",".join(data.hobbies)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created", "id": new_user.id}

@app.get("/api/users")
def get_all_users():
    db: Session = next(get_db())
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "age": u.age,
            "hobbies": u.hobbies.split(","),
            "friends": [f.id for f in u.friends],
            "popularityScore": calc_popularity(u)
        } for u in users
    ]

@app.post("/api/users/{user_id}/link")
def link_users(user_id: str, data: dict):
    db: Session = next(get_db())
    other_id = data.get("other_id")
    user1 = db.query(User).filter(User.id == user_id).first()
    user2 = db.query(User).filter(User.id == other_id).first()

    if not user1 or not user2:
        raise HTTPException(status_code=404, detail="User not found")
    if user2 in user1.friends:
        raise HTTPException(status_code=409, detail="Already friends")

    user1.friends.append(user2)
    db.commit()
    return {"message": "Friendship created"}

@app.delete("/api/users/{user_id}/unlink")
def unlink_users(user_id: str, data: dict):
    db: Session = next(get_db())
    other_id = data.get("other_id")
    user1 = db.query(User).filter(User.id == user_id).first()
    user2 = db.query(User).filter(User.id == other_id).first()

    if not user1 or not user2:
        raise HTTPException(status_code=404, detail="User not found")
    if user2 not in user1.friends:
        raise HTTPException(status_code=404, detail="Not friends")

    user1.friends.remove(user2)
    db.commit()
    return {"message": "Friendship removed"}

@app.delete("/api/users/{user_id}")
def delete_user(user_id: str):
    db: Session = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if len(user.friends) > 0:
        raise HTTPException(status_code=409, detail="User has friends, unlink first")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@app.get("/api/graph")
def get_graph():
    db: Session = next(get_db())
    users = db.query(User).all()
    nodes = []
    edges = []

    for u in users:
        nodes.append({
            "id": u.id,
            "username": u.username,
            "popularityScore": calc_popularity(u)
        })
        for f in u.friends:
            edges.append({"source": u.id, "target": f.id})
    return {"nodes": nodes, "edges": edges}


