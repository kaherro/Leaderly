import unittest
import redis
import psycopg2
from src.bases.db_manager import DBManager

class TestDBManager(unittest.TestCase):
    def setUp(self):
        self.db = DBManager()
        self.db.redis_db.flushdb()
        with self.db.pg_db.cursor() as cur:
            cur.execute("DELETE FROM leaderboard;")
            self.db.pg_db.commit()

    def test_initialization_redis(self):
        with self.assertRaises(AttributeError):  
            db = DBManager(redis_port=99523)
        
        with self.assertRaises(AttributeError):  
            db = DBManager(redis_host='fsa')
    
    def test_initialization_pg(self):
        with self.assertRaises(AttributeError):  
            db = DBManager(pg_password='wrong_host')
        
        with self.assertRaises(AttributeError):  
            db = DBManager(pg_port=25216)

        with self.assertRaises(AttributeError):  
            db = DBManager(pg_host='sab')

        with self.assertRaises(AttributeError):  
            db = DBManager(pg_user='adsvn')

        with self.assertRaises(AttributeError):  
            db = DBManager(pg_dbname='agnkas')    
    
    def test_update_score_new_user(self):
        self.db.update_score("test_user", 100)
        score = self.db.get_score("test_user")
        self.assertEqual(score, 100)
    
    def test_update_score_existing_user(self):
        self.db.update_score("test_user", 100)
        self.db.update_score("test_user", 200)
        score = self.db.get_score("test_user")
        self.assertEqual(score, 200)
    
    def test_update_score_multiple_users(self):
        db = DBManager()
        users = {"user1": 100, "user2": 200, "user3": 300}
        for user, score in users.items():
            self.db.update_score(user, score)
        
        for user, expected_score in users.items():
            score = self.db.get_score(user)
            self.assertEqual(score, expected_score)
    
    def test_get_score_nonexistent_user(self):
        score = self.db.get_score("nonexistent")
        self.assertIsNone(score)
        
    def test_get_leaderboard_all(self):
        scores = [("user1", 300), ("user2", 200), ("user3", 100)]
        for user, score in scores:
            self.db.update_score(user, score)
        leaderboard = self.db.get_leaderboard(0)
        self.assertEqual(len(leaderboard), 3)
    
    def test_get_leaderboard_empty(self):
        leaderboard = self.db.get_leaderboard(10)
        self.assertEqual(leaderboard, [])
    
    def test_update_tags_new_user(self):
        tags = [1.0, 2.0, 3.0]
        self.db.update_tags("test_user", tags)
        
        res = self.db.get_tags("test_user")
        self.assertEqual(res, [str(t) for t in tags]) 
    
    def test_update_tags_existing_user(self):
        self.db.update_score("test_user", 100)
        
        tags = [1.0, 2.0, 3.0]
        self.db.update_tags("test_user", tags)
        
        res = self.db.get_tags("test_user")
        self.assertEqual(res, [str(t) for t in tags])
        
        score = self.db.get_score("test_user")
        self.assertEqual(score, 100)
    
    def test_update_tags_empty_list(self):
        self.db.update_tags("test_user", [1.0, 2.0])
        self.db.update_tags("test_user", [])
        
        res = self.db.get_tags("test_user")
        self.assertEqual(res, [])
    
    def test_get_tags_nonexistent_user(self):
        tags = self.db.get_tags("nonexistent")
        self.assertEqual(tags, [])
    