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
    if action == "connect":
        await websocket.accept()
        active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(active_connections)}")
        
        leaderboard = db_manager.get_leaderboard()
        await websocket.send_json({
            "type": "Connection (successful)",
            "action": "connect",
            "data": [{"key": k, "score": s, "tags": t} for k, s, t in leaderboard]
        })
        
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total connections: {len(active_connections)}")
        return
    
    await websocket.accept()

    try:
        if action == "update_score":
            parts = path.split('/')
            if len(parts) == 2:
                key = parts[0]
                score = float(parts[1])
                
                db_manager.update_score(key, score)
                logger.info(f"Updated {key}'s score to {score}")
                
                await websocket.send_json({
                    "type": "Operation (successful)",
                    "action": "update_score",
                    "key": key,
                    "score": score
                })
                
                await broadcast_leaderboard()
        
        elif action == "update_tags":
            parts = path.split('/')
            if len(parts) == 2:
                key = parts[0]
                tags = [float(tag) for tag in parts[1].split(',')]
                
                db_manager.update_tags(key, tags)
                logger.info(f"Updated {key}'s tags to {tags}")
                
                await websocket.send_json({
                    "type": "Operation (successful)",
                    "action": "update_tags",
                    "key": key,
                    "tags": tags
                })
                
                await broadcast_leaderboard()
        
        elif action == "delete_object":
            key = path
            
            db_manager.delete_object(key)
            logger.info(f"Deleted {key}")
            
            await websocket.send_json({
                "type": "Operation (successful)",
                "action": "delete_object",
                "key": key
            })
            
            await broadcast_leaderboard()
        
        elif action == "get_score":
            key = path
            
            score = db_manager.get_score(key)
            
            await websocket.send_json({
                "type": "Operation (successful)",
                "action": "get_score",
                "key": key,
                "score": score
            })
        
        elif action == "get_tags":
            key = path
            
            tags = db_manager.get_tags(key)
            
            await websocket.send_json({
                "type": "Operation (successful)",
                "action": "get_tags",
                "key": key,
                "tags": tags
            })
        
        elif action == "get_leaderboard":
            n = int(path) if path and path.isdigit() else 0
            
            leaderboard = db_manager.get_leaderboard(n)
            
            await websocket.send_json({
                "type": "Operation (successful)",
                "action": "get_leaderboard",
                "data": [{"key": k, "score": s, "tags": t} for k, s, t in leaderboard]
            })
            
        else:
            await websocket.send_json({
                "type": "error",
                "message": f"Unknown action: {action}"
            })
    
    except Exception as e:
        logger.error(f"Error in ws_handler: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    
    finally:
        await websocket.close()
    
async def broadcast_leaderboard():
    '''Sends the updated leaderboard to all connected clients'''
    if not active_connections:
        return
    
    try:
        leaderboard = db_manager.get_leaderboard()
        message = {
            "type": "leaderboard_update",
            "data": [{"key": k, "score": s, "tags": t} for k, s, t in leaderboard]
        }
        for connection in active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to connection: {e}")
        logger.info(f"Broadcasted leaderboard to {len(active_connections)} clients")
    except Exception as e:
        logger.error(f"Error broadcasting leaderboard: {e}")
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)