def GroupSerializer(group: dict):
    return {
        "id": str(group["_id"]),
        "name": group["name"],
        "members": group["members"],
    }