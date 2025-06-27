from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

app = FastAPI()

# Allow frontend from anywhere (for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dictionary to keep track of connected users by ID
connected_peers: Dict[str, WebSocket] = {}

@app.websocket("/ws/{peer_id}")
async def websocket_endpoint(websocket: WebSocket, peer_id: str):
    await websocket.accept()
    connected_peers[peer_id] = websocket
    print(f"✅ Connected: {peer_id}")

    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("type")
            target = data.get("to")
            payload = data.get("data")

            if event in ["offer", "answer", "ice-candidate"] and target in connected_peers:
                await connected_peers[target].send_json({
                    "type": event,
                    "from": peer_id,
                    "data": payload
                })

    except WebSocketDisconnect:
        print(f"❌ Disconnected: {peer_id}")
        connected_peers.pop(peer_id, None)
