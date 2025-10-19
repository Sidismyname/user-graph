from sqlalchemy import create_engine, Column, String, Integer, DateTime, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
engine = create_engine(DATABASE_URL)
try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")
    
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

friend_table = Table(
    "friendships",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id")),
    Column("friend_id", String, ForeignKey("users.id"))
)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    hobbies = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    friends = relationship(
        "User",
        secondary=friend_table,
        primaryjoin=id == friend_table.c.user_id,
        secondaryjoin=id == friend_table.c.friend_id
    )

def init_db():
    Base.metadata.create_all(bind=engine)


    # def popularity(self,all_users:dict[UUID,"User"]):
    #     shared_hobbies = 0
    #     for friend_id in self.friends:
    #         friend = all_users.get(friend_id)
    #         if friend is not None:
    #             shared_hobbies += len(set(self.hobbies) & set(friend.hobbies))
    #     score = len(self.friends) + (0.5* shared_hobbies)
    #     return score
