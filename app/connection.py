from fastapi import WebSocket


class ConnectionManager:
    """
    Utility class for managing websocket
    connections
    """

    def __init__(self) -> None:
        self.connections = []

    async def connect(self, websocket: WebSocket):
         await websocket.accept()
         self.connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        await websocket.close()
        self.connections.remove(websocket)

    async def broadcast(self, data):
        for connection in self.connections:
            await connection.send_text(data)