from src.leaderboard import LeaderboardClient

lb = LeaderboardClient()
    
lb.update_score("player1", 1500)
lb.update_tags("player1", [1.5, 2.5, 3.5])
score = lb.get_score("player1")
leaderboard = lb.get_leaderboard(10)
lb.delete_object("player1")