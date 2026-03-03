'''
This module defines the DBManager class, 
which provides methods to interact with a Redis database.
'''
from typing import List

import redis
import psycopg2
import logging

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class DBManager:
    '''Manages queries with a Redis database for leaderboard.'''
    def __init__(self, redis_host: str='localhost', redis_port: int=6379, 
                pg_host: str='localhost', pg_port: int=5432, pg_user: str='postgres', 
                pg_password: str='2991', pg_dbname: str='leaderly'):
        '''Initializes the DBManager and connects to Redis and PostgreSQL.'''
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.pg_host = pg_host
        self.pg_port = pg_port
        self.pg_user = pg_user
        self.pg_password = pg_password
        self.pg_dbname = pg_dbname
        self.__connect()
        self.__init_postgres()
        self.__sync_databases()
        
    def __connect(self):
        '''Connects to the Redis and PostgreSQL databases and handles connection errors.'''
        try:
            self.redis_db = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)
            self.redis_db.ping()
            logger.info("Connected to Redis successfully!")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_db = None

        try:
            self.pg_db = psycopg2.connect(
                dbname=self.pg_dbname, 
                user=self.pg_user, 
                password=self.pg_password, 
                host=self.pg_host, 
                port=self.pg_port
            )
            logger.info("Connected to PostgreSQL successfully!")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.pg_db = None


    def __init_postgres(self):
        '''Initializes the PostgreSQL database with the necessary table.'''        
        try:
            cur = self.pg_db.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(255) UNIQUE NOT NULL,
                    score FLOAT NOT NULL,
                    tags FLOAT[]
                );
            ''')
            self.pg_db.commit()
            cur.close()
            logger.info("PostgreSQL database initialized successfully!")
        except psycopg2.Error as e:
            logger.error(f"Error initializing PostgreSQL database: {e}")
            if self.pg_db:
                self.pg_db.rollback()

    def __sync_databases(self):
        '''Synchronizes Redis with PostgreSQL.'''
        try:
            self.redis_db.flushdb()
            cur = self.pg_db.cursor()
            cur.execute('SELECT key, score, tags FROM leaderboard;')
            rows = cur.fetchall()
            for key, score, tags in rows:
                self.redis_db.zadd('leaderboard', {key: score})
                if tags:
                    self.redis_db.delete(key)
                    self.redis_db.lpush(key, *tags)
            cur.close()
            logger.info("Redis synchronized with PostgreSQL successfully!")
        except Exception as e:
            logger.error(f"Error synchronizing Redis with PostgreSQL: {e}")

    def update_score(self, key: str, score: float):
        '''Updates the score for a given key in the leaderboard.'''
        try:
            self.redis_db.zadd('leaderboard', {key: score})
            cur = self.pg_db.cursor()
            cur.execute(f'''
                INSERT INTO leaderboard (key, score) 
                VALUES ('{key}', {score}) 
                ON CONFLICT (key) 
                DO UPDATE SET score = {score};
            ''')
            self.pg_db.commit()
            cur.close()
            logger.info(f"Updated {key}'s score to {score}.")
        except Exception as e:
            logger.error(f"Error updating score: {e}")

    def get_score(self, key: str):
        '''Returns the score for a given key from the leaderboard.'''
        try:
            score = self.redis_db.zscore('leaderboard', key)
            if score is not None:
                logger.info(f"{key}'s score: {score}")
                return score
            else:
                logger.info(f"{key} not found in leaderboard.")
                return None
        except Exception as e:
            logger.error(f"Error retrieving score: {e}")
            return None

    def get_leaderboard(self, n:int = 0):
        '''Returns the top N objects from the leaderboard.
        If n is 0 or not given, returns the entire leaderboard.'''
        try:
            leaderboard = self.redis_db.zrange('leaderboard', 0, n - 1, withscores=True)
            logger.info(f"Top {n} Leaderboard: {leaderboard}")
            return leaderboard
        except Exception as e:
            logger.error(f"Error retrieving leaderboard: {e}")
            return []

    def update_tags(self, key:str, tags:List[float]):
        ''''Updates the tags for a given key. 
        If tags is empty, it clears all tags for that key.'''
        try:
            self.redis_db.delete(key)
            cur = self.pg_db.cursor()
            cur.execute(f'''
                UPDATE leaderboard 
                SET tags = ARRAY{tags} 
                WHERE key = '{key}';
            ''')
            cur.close()
            if tags:
                self.redis_db.lpush(key, *tags)
                logger.info(f"Updated {key}'s tags: {tags}")
            else:
                logger.info(f"Cleared all tags for {key}.")
        except Exception as e:
            logger.error(f"Error updating tags: {e}")

    def delete_object(self, key:str):
        '''Deletes a given key from the leaderboard and its associated tags.'''
        try:
            self.redis_db.zrem('leaderboard', key)
            self.redis_db.delete(key)
            cur = self.pg_db.cursor()
            cur.execute(f'''
                DELETE FROM leaderboard WHERE key = '{key}';
            ''')
            self.pg_db.commit()
            cur.close()
            logger.info(f"Deleted {key} from leaderboard.")
        except Exception as e:
            logger.error(f"Error deleting user: {e}")