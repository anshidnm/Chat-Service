from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    members: list = []


class ChatRoomCreate(BaseModel):
    room_type: str
    group_id: str|None
    users: list = []


class ChatMessageCreate(BaseModel):
    message: str
    sender: int
    room_id: int
