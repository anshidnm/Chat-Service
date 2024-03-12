from bson import ObjectId
from connection import ConnectionManager
from database import chat_room, chat_group, chat_message
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body, WebSocket
from typing import List
from typing_extensions import Annotated
from schemas import (
    GroupCreate,
    ChatRoomSchema,
    ChatMessageSchema
)
from serializers import (
    GroupSerializer,
    RoomSerializer
)

import asyncio


app = FastAPI(title="Chat Module")


socket = ConnectionManager()


@app.post("/group", tags=["Group"])
async def create_group(
    data: GroupCreate
):
    if await chat_group.find({"name": data.name}).to_list(length=None):
        raise HTTPException(400, "This name already exists")
    data.members = list(set(data.members))
    group = await chat_group.insert_one(
        {**data.model_dump(), "created_at": str(datetime.utcnow())}
    )
    new_group = await chat_group.find_one({"_id": group.inserted_id})
    chat_room.insert_one({
        "room_type": "group",
        "group_id": ObjectId(new_group["_id"]),
        "users": [],
        "created_at": str(datetime.utcnow())
    }) 
    return GroupSerializer(new_group)


@app.patch("/add-member/{group_id}/{member}", tags=["Group"])
async def add_member_to_group(
    *,
    group_id: str,
    member: int
):
    group = await chat_group.find_one({"_id": ObjectId(group_id)})
    if not group:
        raise HTTPException(404, "Group not found")
    members = group["members"]
    if member not in group["members"]:
        members.append(member)
        await chat_group.update_one(
            {"_id": ObjectId(group_id)},
            {"$set":{"members": members}}
        )
        group = await chat_group.find_one({"_id": ObjectId(group_id)})
    return GroupSerializer(group)


@app.patch("/remove-member/{group_id}/{member}", tags=["Group"])
async def remove_member_from_group(
    *,
    group_id: str,
    member: int
):
    group = await chat_group.find_one({"_id": ObjectId(group_id)})
    if not group:
        raise HTTPException(404, "Group not found")
    members = group["members"]
    if member in group["members"]:
        members.remove(member)
        await chat_group.update_one(
            {"_id": ObjectId(group_id)},
            {"members": members}
        )
        group = await chat_group.find_one({"_id": ObjectId(group_id)})
    return GroupSerializer(group)


@app.post("/room", tags=["Room"])
async def start_individual_room(
    users: Annotated[list, Body(embed=True)]
):
    if len(users) != 2:
        raise HTTPException(400, "only 2 users allowed")
    if users[0] == users[1]:
        raise HTTPException(400, "users must be different")
    room = await chat_room.find_one({"users": {"$all": users}, "room_type": "normal"})
    if not room:
        inserted_room = await chat_room.insert_one({
            "room_type": "normal",
            "users": users,
            "group_id": None,
            "created_at": str(datetime.utcnow())
        })
        room = await chat_room.find_one({"_id": inserted_room.inserted_id})
    return RoomSerializer(room)


@app.get("/room", tags=["Room"], response_model=List[ChatRoomSchema])
async def list_rooms(
    user_id: int,
    skip: int = 0,
    limit: int = 10
):
    user_groups = await chat_group.find({"members": user_id,}, projection={"_id": 1}).to_list(length=None)
    group_ids = [group["_id"] for group in user_groups]
    rooms = await (
        chat_room
        .find({"$or": [{"users": user_id}, {"group_id": {"$in": group_ids}}]})
        .limit(limit)
        .skip(skip)
        .sort("_id", -1)
        .to_list(length=None)
    )
    for room in rooms:
        room.update(
            {
                "id": str(room["_id"]),
                "group_id": str(room["group_id"]) if room["group_id"] else None,
            }
        )
    return rooms


@app.get(
        "/message",
        response_model=List[ChatMessageSchema],
        tags=["Message"]
    )
async def list_chat_message(
    room_id: str,
    skip: int = 0,
    limit: int = 10
):
    chats = await (
        chat_message
        .find({"room_id": ObjectId(room_id)})
        .skip(skip)
        .limit(limit)
        .sort("_id", 1)
        .to_list(length=None)
    )
    for chat in chats:
        chat.update(
            {
                "id": str(chat["_id"]),
                "room_id": str(chat["room_id"])
            }
        )
    return chats


@app.websocket("/ws/{room_id}/{user_id}")
async def connect_room(
    websocket: WebSocket,
    room_id: str,
    user_id: str
):
    try:
        await socket.connect(websocket)
        while True:
            data = await websocket.receive_text()
            insertion = chat_message.insert_one({
                "room_id": ObjectId(room_id),
                "user_id": user_id,
                "message": data,
                "created_at": str(datetime.utcnow())
            })
            broadcasting =  socket.broadcast(f"{user_id}: {data}")
            await asyncio.gather(insertion, broadcasting)
    except:
        await socket.disconnect(websocket)