from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_peers: Dict[str, WebSocket] = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    peer_id = None

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            # 1. Register new peer
            if event_type == "register":
                peer_id = data.get("name")
                connected_peers[peer_id] = websocket
                print(f"✅ Registered: {peer_id}")
                # Send online user list to all
                await broadcast_user_list()

            # 2. Handle offer/answer/ice-candidate
            elif event_type in ["offer", "answer", "ice-candidate"]:
                target = data.get("to")
                if target in connected_peers:
                    await connected_peers[target].send_json({
                        "type": event_type,
                        "from": peer_id,
                        "data": data.get("data")
                    })

    except WebSocketDisconnect:
        print(f"❌ Disconnected: {peer_id}")
        if peer_id and peer_id in connected_peers:
            connected_peers.pop(peer_id)
            await broadcast_user_list()


# Helper to broadcast list of all online users
async def broadcast_user_list():
    user_list = list(connected_peers.keys())
    for ws in connected_peers.values():
        await ws.send_json({ "type": "online-users", "users": user_list })
