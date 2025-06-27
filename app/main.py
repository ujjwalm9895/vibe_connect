from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in clients:
                if client != websocket:
                    await client.send_text(data)
    except Exception:
        clients.remove(websocket)
        await websocket.close()

@socket.on('call-user')
def call_user(data):
    emit('incoming-call', room=data['to'], data=...offer...)

@socket.on('answer-call')
def answer_call(data):
    emit('call-accepted', room=data['to'], data=...answer...)

@socket.on('ice-candidate')
def handle_ice(data):
    emit('ice-candidate', room=data['to'], data=data['candidate'])
