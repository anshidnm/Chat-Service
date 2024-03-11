from bson import ObjectId
from database import chat_room, chat_group
from fastapi import FastAPI, HTTPException, Body
from typing import List
from typing_extensions import Annotated
from schemas import (
    GroupCreate,
    ChatRoomSchema
)
from serializers import (
    GroupSerializer,
    RoomSerializer
)


app = FastAPI(title="Chat Module")


@app.post("/group", tags=["Group"])
async def create_group(
    data: GroupCreate
):
    if await chat_group.find({"name": data.name}).to_list(length=None):
        raise HTTPException(400, "This name already exists")
    data.members = list(set(data.members))
    group = await chat_group.insert_one(data.model_dump())
    new_group = await chat_group.find_one({"_id": group.inserted_id})
    chat_room.insert_one({
        "room_type": "group",
        "group_id": ObjectId(new_group["_id"]),
        "users": []
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
    room = await chat_room.find_one({"users": {"$all": users}})
    if not room:
        inserted_room = await chat_room.insert_one({
            "room_type": "normal",
            "users": users,
            "group_id": None
        })
        room = await chat_room.find_one({"_id": inserted_room.inserted_id})
    return RoomSerializer(room)


@app.get("/room", tags=["Room"], response_model=List[ChatRoomSchema])
async def list_rooms(
    user_id: str,
    skip: int = 0,
    limit: int = 10
):
    user_groups = await chat_group.find({"members": user_id,}, projection={"_id": 1}).to_list(length=None)
    print(user_groups)
    rooms = await (
        chat_room
        .find({"users":user_id, })
        .limit(limit)
        .skip(skip)
        .sort("_id", -1)
        .to_list(length=None)
    )
    for room in rooms:
        room.update({"id": str(room["_id"])})
    return rooms