from motor import motor_asyncio


MONGO_DETAILS = "mongodb://root:1234@db:27017"

client = motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.chatapp

chat_group = database.get_collection("group_collections")
chat_room = database.get_collection("chat_room_collections")
chat_message = database.get_collection("chat_message_collections")