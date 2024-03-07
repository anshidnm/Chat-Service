from bson import ObjectId
from database import chat_message, chat_group
from fastapi import FastAPI, HTTPException, Body
from typing_extensions import Annotated
from schemas import (
    GroupCreate
)
from serializers import (
    GroupSerializer
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
