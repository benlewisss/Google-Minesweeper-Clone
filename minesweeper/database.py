import sqlite3
from sqlite3 import Error
import datetime
import random

#print("\033c")

def take_score(elem):
    return elem[1]

class Database():
	def __init__(self, db_file):
		self.timestamp = datetime.datetime.now()
		self.db_file = db_file
		self.conn = self.initiate_connection()
		if self.conn is not None:
			self.create_tables()
		else:
			print("ERROR: Cannot connet to database.")

	def initiate_connection(self):
		# :return: Returns connection object, or None if connection failed
		# :return_format: return = connection
		connection = None
		try:
			connection = sqlite3.connect(self.db_file)
			return connection
		except Error as err:
			print("connection error:")
			print(err)

		return connection

	def create_tables(self):
		conn = self.conn
		
		# SQL to create the users table
		sql_users_table = """CREATE TABLE IF NOT EXISTS users(
							id integer NOT NULL PRIMARY KEY,
							username text NOT NULL,
							join_date timestamp NOT NULL)
							"""

		# SQL to create the scores table
		sql_scores_table = """CREATE TABLE IF NOT EXISTS scores(
							id integer NOT NULL PRIMARY KEY,
							score integer NOT NULL,
							date timestamp NOT NULL,
							difficulty integer NOT NULL,
							user_id integer NOT NULL,
							FOREIGN KEY (user_id) REFERENCES users (id))
							"""
		try:
			cur = conn.cursor()
			cur.execute(sql_users_table)
			cur.execute(sql_scores_table)
		except Error as err:
			print("create_tables error:")
			print(err)

	def create_user(self, username):
		# :param: Username of the user creating/logging into an account (users.username)
		# :return: ID of the user (users.id)
		# :return_format: return = id

		conn = self.conn

		cur = conn.cursor()

		sql_insert_user = """ INSERT INTO users(username, join_date) VALUES(?,?) """
		user_tuple = (username, self.timestamp)
		
		cur.execute("SELECT * FROM users WHERE username=?", (username,))
		if cur.fetchall():
			pass
		else:
			cur.execute(sql_insert_user, user_tuple)
			
		conn.commit()

		cur.execute("SELECT * FROM users WHERE username=?", (username,))
		return cur.fetchone()[0]
		

	def submit_score(self, score, difficulty, user_id):
		# :param: Score of the entry to be submitted @database.scores.score
		# :param: ID of the user submitting the score @database.users.id
		# :return: Either 0 if the score is 0, or the ID of the score entry. 
		# :return_format: return = id

		conn = self.conn

		cur = conn.cursor()

		sql = """ INSERT INTO scores(score, difficulty, date, user_id)
				VALUES(?,?,?,?) """

		if score >= 1:
			user_tuple = (score, difficulty, self.timestamp, user_id)
			cur.execute(sql, user_tuple)
			conn.commit()
			return cur.lastrowid
		else:
			return None

	def get_all_data(self):
		conn = self.conn

		cur = conn.cursor()

		sql_users_query = """ SELECT * FROM users """
		sql_scores_query = """ SELECT * FROM scores ORDER BY difficulty ASC"""
		
		cur.execute(sql_users_query)
		records = cur.fetchall()
		print("Users:")
		# Print Records
		for record in records:
			print(record)

		cur.execute(sql_scores_query)
		records = cur.fetchall()
		print("\nScores:")
		# Print Records
		for record in records:
			print(record)  

	def get_leaderboard(self):
		# :return: list[0,1,2] is difficulty 0,1,2 respectively. list[x][0,1,2] is the top 3 scores for that difficulty 
		#          respectively, list[x][x][0,1,2] is user_id, score and date respectively
		# :return_format: [[(username, highscore, difficulty, timestamp)], [(username, highscore, difficulty, timestamp)], etc...]}
		conn = self.conn

		cur = conn.cursor()

		sql_query = """ SELECT user_id, MIN(score), date 
						FROM scores 
						WHERE difficulty=? 
						GROUP BY user_id 
						ORDER BY score ASC 
						LIMIT 3"""

		leaderboard = []
		for difficulty in range(3):
			cur.execute(sql_query,(difficulty,))
			results = cur.fetchall()
			leaderboard.append(results)

		return leaderboard

	def get_highscore(self, difficulty, user_id):
		# :param: Difficulty of the game to retrieve a highscore for
		# :param: ID of the user retrieving their highscore SQL@users.id
		# :return: Tuple containing the highscore and the timestamp when it was achieved.
		# :return_format: return = (score, difficulty, timestamp)

		conn = self.conn

		cur = conn.cursor()

		cur.execute("SELECT MIN(score), difficulty, date FROM scores WHERE user_id=? AND difficulty=?", (user_id,difficulty,))
		result = cur.fetchone()
		return result

	def get_user(self, user_id):
		# :param: ID of the user retrieving their highscore SQL@users.id
		# :return: Tuple containing data relating to a user.
		# :return_format: return = (id, username, join_date)

		conn = self.conn

		cur = conn.cursor()

		cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
		result = cur.fetchone() 
		return result

	def purge_data(self):
		conn = self.conn

		# Define Queries
		sql_delete_users = """DELETE FROM users"""
		sql_delete_scores = """DELETE FROM scores"""

		try:
			cur = conn.cursor()
			cur.execute(sql_delete_users)
			cur.execute(sql_delete_scores)
		except Error as err:
			print("purge_data error:")
			print(err)
		
		conn.commit()
		
		


# db = Database("data/database.sqlite")

# print(db.get_user(3))

# db.purge_data()

# userID1 = db.create_user("Zephos")
# print("UserID:",userID1)
# db.submit_score(random.randint(5, 150), random.randint(0, 2), userID1)
# print("HIGHSCORE:",db.get_highscore(1,userID1))

# userID2 = db.create_user("SkilledMan420")
# print("UserID:",userID2)
# db.submit_score(random.randint(5, 150), random.randint(0, 2), userID2)
# print("HIGHSCORE:",db.get_highscore(2,userID2))

# userID3 = db.create_user("Skillplayer99")
# print("UserID:",userID3)
# db.submit_score(random.randint(5, 150), print(random.randint(0, 2)), userID3)
# print(db.get_highscore(userID3))

# print("\nAll Data:")
# db.get_all_data()

# print("\nLeaderboard:")
# leaderboard = db.get_leaderboard()
# print(leaderboard)

# print("\nName:")
# specific = db.get_user(leaderboard[1][0][0])[1]
# print(specific)