from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Set
import logging

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.bases.db_manager import DBManager

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()

db_manager = DBManager()

active_connections: Set[WebSocket] = set()

@app.websocket("/ws/{action}/{path:path}")
async def ws_handler(websocket: WebSocket, action: str, path: str):
    """WebSocket handling function that processes different 
    API-actions based on the URL path."""
    if action == "get_leaderboard":
        await websocket.accept()
        active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(active_connections)}")
        
        leaderboard = db_manager.get_leaderboard()
        await websocket.send_json({
            "type": "success",
            "action": "leaderboard",
            "data": [{"key": k, "score": s, "tags": t} for k, s, t in leaderboard]
        })
        
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total connections: {len(active_connections)}")
        return
    
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)