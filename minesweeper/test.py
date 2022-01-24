import dataManagement

leaderboard = dataManagement.leaderboard()
username, bestScore, bestScoreDate, bestScoreTime = leaderboard.bestScores("hard")
print(username)
print(bestScore)
print(bestScoreDate)
print(bestScoreTime)