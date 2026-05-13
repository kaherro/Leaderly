import unittest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

from src.api.ws_api import app, active_connections, db_manager

class TestWebSocketAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        active_connections.clear()
        db_manager.redis_db.flushdb()
        with db_manager.pg_db.cursor() as cur:
            cur.execute("DELETE FROM leaderboard;")
            db_manager.pg_db.commit()
    
    def tearDown(self):
        active_connections.clear()
        db_manager.redis_db.flushdb()
        with db_manager.pg_db.cursor() as cur:
            cur.execute("DELETE FROM leaderboard;")
            db_manager.pg_db.commit()
    
    def test_connect(self):
        with self.client.websocket_connect("/ws/connect/test") as ws:
            data = ws.receive_json()
            self.assertEqual(data["type"], "Connection (successful)")
    
    def test_update_score(self):
        with self.client.websocket_connect("/ws/update_score/player1/100") as ws:
            data = ws.receive_json()
            self.assertEqual(data["action"], "update_score")
            self.assertEqual(data["score"], 100.0)
    
    def test_update_tags(self):
        with self.client.websocket_connect("/ws/update_tags/player1/1.0,2.0,3.0") as ws:
            data = ws.receive_json()
            self.assertEqual(data["action"], "update_tags")
            self.assertEqual(data["tags"], [1.0, 2.0, 3.0])
    
    def test_delete_object(self):
        db_manager.update_score("delete_me", 100)
        with self.client.websocket_connect("/ws/delete_object/delete_me") as ws:
            data = ws.receive_json()
            self.assertEqual(data["action"], "delete_object")
            self.assertEqual(data["key"], "delete_me")
    
    def test_get_score(self):
        db_manager.update_score("player1", 500)
        with self.client.websocket_connect("/ws/get_score/player1") as ws:
            data = ws.receive_json()
            self.assertEqual(data["action"], "get_score")
            self.assertEqual(data["score"], 500)
    
    def test_get_tags(self):
        db_manager.update_tags("player1", [1.0, 2.0])
        with self.client.websocket_connect("/ws/get_tags/player1") as ws:
            data = ws.receive_json()
            self.assertEqual(data["action"], "get_tags")
            self.assertEqual(data["tags"], ["1.0", "2.0"])
    
    def test_get_leaderboard_all(self):
        db_manager.update_score("player1", 300)
        db_manager.update_score("player2", 200)
        with self.client.websocket_connect("/ws/get_leaderboard/0") as ws:
            data = ws.receive_json()
            self.assertEqual(data["action"], "get_leaderboard")
            self.assertEqual(len(data["data"]), 2)
    
    def test_get_leaderboard_limit(self):
        for i in range(5):
            db_manager.update_score(f"player{i}", 1000 - i * 100)
        with self.client.websocket_connect("/ws/get_leaderboard/3") as ws:
            data = ws.receive_json()
            self.assertEqual(len(data["data"]), 3)
    
    def test_broadcast_on_update(self):
        with self.client.websocket_connect("/ws/connect/listener") as listener:
            listener.receive_json() 
            with self.client.websocket_connect("/ws/update_score/broadcast/100") as updater:
                updater.receive_json()
                broadcast = listener.receive_json()
                self.assertEqual(broadcast["type"], "leaderboard_update")
    
    def test_unknown_action(self):
        with self.client.websocket_connect("/ws/abracadabra/abeme") as ws:
            data = ws.receive_json()
            self.assertEqual(data["type"], "error")

if __name__ == "__main__":
    unittest.main()