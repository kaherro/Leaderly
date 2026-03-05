import unittest
import redis
import psycopg2
from src.bases.db_manager import DBManager

class DBManagerTests(unittest.TestCase):
    def test_1(self):
        self.assertEqual('1','1')

    def test_initialization_success(self):
        db = DBManager()
        self.assertIsNotNone(db.redis_db)
        self.assertIsNotNone(db.pg_db)

    
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
