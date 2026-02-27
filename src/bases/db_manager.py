'''
This module defines the DBManager class, 
which provides methods to interact with a Redis database.
'''
import redis
import logging

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
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
        
    def _connect(self):
        '''Connects to the Redis database and handles connection errors.'''
        try:
            self.r = redis.Redis(host=self.host, port=self.port, decode_responses=True)
            self.r.ping()
            logger.info("Connected to Redis successfully!")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.r = None

    def refresh_score(self, key: str, score: float):
        '''Updates the score for a given key in the leaderboard.'''
        try:
            self.r.zadd('leaderboard', {key: score})
            logger.info(f"Updated {key}'s score to {score}.")
        except Exception as e:
            logger.error(f"Error updating score: {e}")

    def get_score(self, key: str):
        '''Returns the score for a given key from the leaderboard.'''
        try:
            score = self.r.zscore('leaderboard', key)
            if score is not None:
                logger.info(f"{key}'s score: {score}")
                return score
            else:
                logger.info(f"{key} not found in leaderboard.")
                return None
        except Exception as e:
            logger.error(f"Error retrieving score: {e}")
            return None

    def get_leaderboard(self, n:int=0):
        '''Returns the top N objects from the leaderboard.
        If n is 0 or not given, returns the entire leaderboard.'''
        try:
            leaderboard = self.r.zrange('leaderboard', 0, n - 1, withscores=True)
            logger.info(f"Top {n} Leaderboard: {leaderboard}")
            return leaderboard
        except Exception as e:
            logger.error(f"Error retrieving leaderboard: {e}")
            return []

    def refresh_tags(self, key:str, tags:list):
        ''''Updates the tags for a given key. 
        If tags is empty, it clears all tags for that key.'''
        try:
            self.r.delete(key)
            if tags:
                self.r.lpush(key, *tags)
                logger.info(f"Updated {key}'s tags: {tags}")
            else:
                logger.info(f"Cleared all tags for {key}.")
        except Exception as e:
            logger.error(f"Error updating tags: {e}")

    def delete_object(self, key:str):
        '''Deletes a given key from the leaderboard and its associated tags.'''
        try:
            self.r.zrem('leaderboard', key)
            self.r.delete(key)
            logger.info(f"Deleted {key} from leaderboard.")
        except Exception as e:
            logger.error(f"Error deleting user: {e}")