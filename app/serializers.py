"""
Json serializers for collections
"""

def GroupSerializer(group: dict):
    return {
        "id": str(group["_id"]),
        "name": group["name"],
        "members": group["members"],
    }

def RoomSerializer(room: dict):
    return {
        "id": str(room["_id"]),
        "room_type":room["room_type"],
        "group_id": room["group_id"],
        "users": room["users"],
    }