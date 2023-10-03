import sqlite3
from sqlite3 import Error
import datetime

class Database:
    """
    A class to manage a SQLite database for a Minesweeper game.

    Attributes:
        db_file (str): The path to the SQLite database file.
        conn (sqlite3.Connection): The database connection.
        timestamp (datetime.datetime): The current timestamp.
    """

    def __init__(self, db_file):
        """
        Initializes the Database object.

        Args:
            db_file (str): The path to the SQLite database file.
        """
        self.db_file = db_file
        self.conn = self.initiate_connection()
        self.timestamp = datetime.datetime.now()

    def initiate_connection(self):
        """
        Establishes a database connection.

        Returns:
            sqlite3.Connection or None: The database connection or None if connection failed.
        """
        try:
            return sqlite3.connect(self.db_file)
        except Error as err:
            print("initiate_connection error:")
            print(err)
            return None

    def create_tables(self):
        """
        Creates 'users' and 'scores' tables if they don't exist in the database.
        """
        conn = self.conn
        sql_users_table = """CREATE TABLE IF NOT EXISTS users(
                            id INTEGER NOT NULL PRIMARY KEY,
                            username TEXT NOT NULL,
                            join_date TIMESTAMP NOT NULL)
                            """
        sql_scores_table = """CREATE TABLE IF NOT EXISTS scores(
                            id INTEGER NOT NULL PRIMARY KEY,
                            score INTEGER NOT NULL,
                            date TIMESTAMP NOT NULL,
                            difficulty INTEGER NOT NULL,
                            user_id INTEGER NOT NULL,
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
        """
        Creates a user and returns their ID if the user doesn't already exist.

        Args:
            username (str): The username of the user.

        Returns:
            int or None: The ID of the user or None if the user already exists.
        """
        conn = self.conn
        cur = conn.cursor()
        sql_insert_user = """INSERT INTO users(username, join_date) VALUES (?, ?)"""
        user_tuple = (username, self.timestamp)
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        if not cur.fetchone():
            cur.execute(sql_insert_user, user_tuple)
        conn.commit()
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        return cur.fetchone()[0]

    def submit_score(self, score, difficulty, user_id):
        """
        Submits a score and returns the ID of the score entry if the score is greater than or equal to 1.

        Args:
            score (int): The score to submit.
            difficulty (int): The difficulty level of the game.
            user_id (int): The user's ID.

        Returns:
            int or None: The ID of the score entry or None if the score is less than 1.
        """
        conn = self.conn
        cur = conn.cursor()
        sql = """INSERT INTO scores(score, difficulty, date, user_id) VALUES (?, ?, ?, ?)"""
        if score >= 1:
            user_tuple = (score, difficulty, self.timestamp, user_id)
            cur.execute(sql, user_tuple)
            conn.commit()
            return cur.lastrowid
        else:
            return None

    def get_all_data(self):
        """
        Retrieves and prints all user and score data from the database.
        """
        conn = self.conn
        cur = conn.cursor()
        sql_users_query = """SELECT * FROM users"""
        sql_scores_query = """SELECT * FROM scores ORDER BY difficulty ASC"""
        cur.execute(sql_users_query)
        users_records = cur.fetchall()
        print("Users:")
        for record in users_records:
            print(record)
        cur.execute(sql_scores_query)
        scores_records = cur.fetchall()
        print("\nScores:")
        for record in scores_records:
            print(record)

    def get_leaderboard(self):
        """
        Retrieves the top 3 scores for each difficulty level from the database.

        Returns:
            list: A list of lists, where each inner list contains user information, highscore, difficulty, and timestamp.
        """
        conn = self.conn
        cur = conn.cursor()
        sql_query = """SELECT user_id, MIN(score), date FROM scores 
                       WHERE difficulty=? GROUP BY user_id 
                       ORDER BY score ASC LIMIT 3"""
        leaderboard = []
        for difficulty in range(3):
            cur.execute(sql_query, (difficulty,))
            results = cur.fetchall()
            leaderboard.append(results)
        return leaderboard

    def get_highscore(self, difficulty, user_id):
        """
        Retrieves the highscore for a specific difficulty and user.

        Args:
            difficulty (int): The difficulty level of the game.
            user_id (int): The user's ID.

        Returns:
            tuple or None: A tuple containing the highscore and timestamp, or None if no highscore is found.
        """
        conn = self.conn
        cur = conn.cursor()
        cur.execute("SELECT MIN(score), date FROM scores WHERE user_id=? AND difficulty=?", (user_id, difficulty,))
        result = cur.fetchone()
        if result:
            return result[0], difficulty, result[1]

    def get_user(self, user_id):
        """
        Retrieves user data by user ID.

        Args:
            user_id (int): The user's ID.

        Returns:
            tuple or None: A tuple containing user information (id, username, join_date), or None if the user doesn't exist.
        """
        conn = self.conn
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
        return cur.fetchone()

    def purge_data(self):
        """
        Deletes all user and score data from the database.
        """
        conn = self.conn
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