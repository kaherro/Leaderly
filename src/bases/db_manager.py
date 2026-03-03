'''
This module defines the DBManager class, 
which provides methods to interact with a Redis database.
'''
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
    def __init__(self, host: str='localhost', port: int=6379):
        '''Initializes the DBManager and connects to Redis.'''
        self.host = host
        self.port = port
        self._connect()
        self.__init_postgres()
        
    def _connect(self):
        '''Connects to the Redis and PostgreSQL databases and handles connection errors.'''
        try:
            self.redis_db = redis.Redis(host=self.host, port=self.port, decode_responses=True)
            self.redis_db.ping()
            logger.info("Connected to Redis successfully!")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_db = None

        try:
            self.pg_db = psycopg2.connect(
                dbname="leaderly", 
                user="postgres", 
                password="2991", 
                host="127.0.0.1", 
                port="5432"
            )
            logger.info("Connected to PostgreSQL successfully!")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.pg_db = None

    def __init_postgres(self):
        '''Initializes the PostgreSQL database with the necessary table.'''
        if self.pg_db is None:
            logger.error("PostgreSQL connection not established.")
            return
        
        try:
            cursor = self.pg_db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(255) UNIQUE NOT NULL,
                    score FLOAT NOT NULL,
                    tags INTEGER[]
                );
            ''')
            self.pg_db.commit()
            cursor.close()
            logger.info("PostgreSQL database initialized successfully!")
        except psycopg2.Error as e:
            logger.error(f"Error initializing PostgreSQL database: {e}")
            if self.pg_db:
                self.pg_db.rollback()

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

    def update_tags(self, key:str, tags:list):
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
            logger.info(f"Deleted {key} from leaderboard.")
        except Exception as e:
            logger.error(f"Error deleting user: {e}")