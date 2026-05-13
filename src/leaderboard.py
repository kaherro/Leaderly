from src.bases.db_manager import DBManager


class LeaderboardClient(DBManager):
    """
    Это класс-обертка для работы с лидербордом, который полностью наследует все методы DBManager.
    Он нужен только для удобства создания клиента пользователем

    Пример использования:
        from leaderboard import LeaderboardClient
        
        lb = LeaderboardClient()
        
        lb.update_score("player1", 1500)
        lb.update_tags("player1", [1.5, 2.5, 3.5])
        score = lb.get_score("player1")
        leaderboard = lb.get_leaderboard(10)
        lb.delete_object("player1")
    """
    
    def __init__(self, 
                redis_host: str = 'localhost', 
                redis_port: int = 6379,
                pg_host: str = 'localhost', 
                pg_port: int = 5432, 
                pg_user: str = 'postgres',
                pg_password: str = '2991', 
                pg_dbname: str = 'leaderly'):
        super().__init__(
            redis_host=redis_host,
            redis_port=redis_port,
            pg_host=pg_host,
            pg_port=pg_port,
            pg_user=pg_user,
            pg_password=pg_password,
            pg_dbname=pg_dbname
        )
