import asyncio
import websockets
import json

class Client:
    def __init__(self, uri):
        self.uri = uri
        self.content = ""
        self.version = 0

    async def connect(self):
        self.ws = await websockets.connect(self.uri)
        
    async def send_operation(self, operation):
        await self.ws.send(json.dumps(operation))
        
    async def receive_updates(self):
        while True:
            message = await self.ws.recv()
            data = json.loads(message)
            self.content = data["content"]
            self.version = data["version"]
            print(f"New content: {self.content}")

if __name__ == "__main__":
    # Run server: uvicorn server:app --reload
    
    # In terminal 1:
    async def client1():
        client = Client("ws://localhost:8000/ws/doc1")
        await client.connect()
        
        # Insert operation
        await client.send_operation({
            "type": "insert",
            "position": 0,
            "char": "H"
        })
        await client.receive_updates()
    
    asyncio.run(client1())
    
    # In terminal 2:
    async def client2():
        client = Client("ws://localhost:8000/ws/doc1")
        await client.connect()
        await client.receive_updates()
        
    asyncio.run(client2())