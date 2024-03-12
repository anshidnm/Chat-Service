from bson import ObjectId
from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    members: list = []


class ChatRoomCreate(BaseModel):
    room_type: str
    group_id: str|None
    users: list = []


class ChatRoomSchema(BaseModel):
    id: str
    room_type: str
    group_id: str|None
    users: list = []
    

class ChatMessageCreate(BaseModel):
    message: str
    sender: int
    room_id: int


class ChatMessageSchema(BaseModel):
    id: str
    room_id: str
    message: str