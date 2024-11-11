# server.py
from fastapi import FastAPI, WebSocket
from typing import List, Dict
import json

app = FastAPI()

class Document:
    def __init__(self):
        self.content = ""
        self.version = 0
        self.operations = []  # Store operation history

    def apply_operation(self, operation):
        if operation["type"] == "insert":
            pos = operation["position"]
            char = operation["char"]
            self.content = self.content[:pos] + char + self.content[pos:]
        elif operation["type"] == "delete":
            pos = operation["position"]
            self.content = self.content[:pos] + self.content[pos + 1:]
        self.version += 1
        self.operations.append(operation)

class DocumentManager:
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.connections: Dict[str, List[WebSocket]] = {}

    def get_or_create_document(self, doc_id: str) -> Document:
        if doc_id not in self.documents:
            self.documents[doc_id] = Document()
        return self.documents[doc_id]

doc_manager = DocumentManager()

@app.websocket("/ws/{doc_id}")
async def websocket_endpoint(websocket: WebSocket, doc_id: str):
    await websocket.accept()
    
    # Add connection to document's connection pool
    if doc_id not in doc_manager.connections:
        doc_manager.connections[doc_id] = []
    doc_manager.connections[doc_id].append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            operation = json.loads(data)
            
            # Get document
            doc = doc_manager.get_or_create_document(doc_id)
            
            # Apply operation
            doc.apply_operation(operation)
            
            # Broadcast to all other clients
            for conn in doc_manager.connections[doc_id]:
                if conn != websocket:
                    await conn.send_text(json.dumps({
                        "operation": operation,
                        "version": doc.version,
                        "content": doc.content
                    }))
    except:
        doc_manager.connections[doc_id].remove(websocket)

if __name__ == "__main__":
    pass
    # Run server: uvicorn server:app --reload
    
    # In terminal 1:
    # async def client1():
    #     client = Client("ws://localhost:8000/ws/doc1")
    #     await client.connect()
        
    #     # Insert operation
    #     await client.send_operation({
    #         "type": "insert",
    #         "position": 0,
    #         "char": "H"
    #     })
    #     await client.receive_updates()
    
    # asyncio.run(client1())
    
    # # In terminal 2:
    # async def client2():
    #     client = Client("ws://localhost:8000/ws/doc1")
    #     await client.connect()
    #     await client.receive_updates()
    
    # asyncio.run(client2())