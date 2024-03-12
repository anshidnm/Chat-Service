"""
Json serializers for collections
"""

def GroupSerializer(group: dict):
    return {
        "id": str(group["_id"]),
        "name": group["name"],
        "members": group["members"],
        "created_at": group["created_at"]
    }

def RoomSerializer(room: dict):
    return {
        "id": str(room["_id"]),
        "room_type":room["room_type"],
        "group_id": room["group_id"],
        "users": room["users"],
        "created_at": room["created_at"],
    }