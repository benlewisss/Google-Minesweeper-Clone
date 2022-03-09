# SQL Leaderboard Database

import sqlite3

class Database():
    def __init__(self):

        # Creates/Connects to Database
        conn = sqlite3.connect("data/database.db")

        # Create Cursor
        c = conn.cursor()

        # Create Tables
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            id integer NOT NULL PRIMARY KEY,
            name text NOT NULL,
            username text NOT NULL)
            """)

        c.execute("""CREATE TABLE IF NOT EXISTS scores(
            user_id integer NOT NULL PRIMARY KEY,
            score integer NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id))
            """)

        # Commit Changes
        conn.commit()

        # Close Connection
        conn.close()

    def entry_check(self, username):
        # Creates/Connects to Database
        conn = sqlite3.connect("data/database.db")
        # Create Cursor
        c = conn.cursor()
        
        # Execute Query
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        results = c.fetchone()
        if results:
            result = True
        else:
            result = False


        # Commit Changes
        conn.commit()

        # Close Connection
        conn.close()

        return result

    def create_user(self, user):
        # Creates/Connects to Database
        conn = sqlite3.connect("data/database.db")
        # Create Cursor
        c = conn.cursor()

        if not self.entry_check(user[1]):
            # Define Query
            sql = """ INSERT INTO users(name,username) VALUES(?,?) """
            
            # Execute Query
            c.execute(sql, user)


        c.execute("SELECT * FROM users WHERE username=?", (user[1],))
        results = c.fetchone()

        # Commit Changes
        conn.commit()

        # Close Connection
        conn.close()

        return results[0]

    def submit_score(self, results):
        # Creates/Connects to Database
        conn = sqlite3.connect("data/database.db")
        # Create Cursor
        c = conn.cursor()

        c.execute("SELECT * FROM scores WHERE user_id=?", (results[0],))
        exist = c.fetchone()
        if exist:
            if (results[1] < exist[2]) or (exist[2] == 0):
                c.execute("DELETE FROM scores WHERE user_id=?", (results[0],))
                sql = """ INSERT INTO scores(user_id,score) VALUES(?,?)"""
                c.execute(sql, results)

        else:
            sql = """ INSERT INTO scores(user_id,score) VALUES(?,?)"""
            c.execute(sql, results)
        

        # Commit Changes
        conn.commit()

        # Close Connection
        conn.close()

    def get_score(self, user_id):
        # Creates/Connects to Database
        conn = sqlite3.connect("data/database.db")
        # Create Cursor
        c = conn.cursor()
        
        # Execute Query
        c.execute("SELECT * FROM scores WHERE user_id=?", (user_id,))
        record = c.fetchone()
        if record == None:
            record = 0
        else:
            record = record[2]

        # Commit Changes
        conn.commit()

        # Close Connection
        conn.close()

        return record

    def get_id(self, username):
        # Creates/Connects to Database
        conn = sqlite3.connect("data/database.db")
        # Create Cursor
        c = conn.cursor()
        
        # Execute Query
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        record = c.fetchone()[0]

        # Commit Changes
        conn.commit()

        # Close Connection
        conn.close()

        return record

    def get_username(self, user_id):
        # Creates/Connects to Database
        conn = sqlite3.connect("data/database.db")
        # Create Cursor
        c = conn.cursor()
        
        # Execute Query
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        record = c.fetchone()[2]

        # Commit Changes
        conn.commit()

        # Close Connection
        conn.close()

        return record

    def get_leaderboard(self):
        # Creates/Connects to Database
        conn = sqlite3.connect("data/database.db")
        # Create Cursor
        c = conn.cursor()

        # Define Query
        sql = """ SELECT * FROM scores ORDER BY score ASC LIMIT 10"""

        leaderboard = []
        
        # Execute Query
        c.execute(sql)
        records = c.fetchall()

        # Print Records
        for record in records:
            c.execute("SELECT * FROM users WHERE id=?", (record[1],))
            user = c.fetchone()
            username = user[2]
            highscore = record[2]
            leaderboard.append([username, highscore])

        # Commit Changes
        conn.commit()

        # Close Connection
        conn.close()
        
        return leaderboard

        
    def show_all_data(self):
        # Creates/Connects to Database
        conn = sqlite3.connect("data/database.db")
        # Create Cursor
        c = conn.cursor()

        # Define Query
        sql = """ SELECT * FROM scores ORDER BY score ASC LIMIT 10"""
        
        # Execute Query
        c.execute(sql)
        records = c.fetchall()

        # Print Records
        for record in records:
            c.execute("SELECT * FROM users WHERE id=?", (record[1],))
            user = c.fetchone()
            print("Username: {}".format(user[2]))
            print("Highscore: {}\n".format(record[2]))

        # Commit Changes
        conn.commit()

        # Close Connection
        conn.close()

    def purge_users(self):

        # Creates/Connects to Database
        conn = sqlite3.connect("data/database.db")
        # Create Cursor
        c = conn.cursor()

        # Define Query
        sql = """ DELETE FROM users """
        
        # Execute Query
        c.execute(sql)

        # Commit Changes
        conn.commit()

        # Close Connection
        conn.close()

    def purge_scores(self):
        # Creates/Connects to Database
        conn = sqlite3.connect("data/database.db")
        # Create Cursor
        c = conn.cursor()

        # Define Query
        sql = """ DELETE FROM scores """
        
        # Execute Query
        c.execute(sql)

        # Commit Changes
        conn.commit()

        # Close Connection
        conn.close()

    def purge(self):
        self.purge_scores()
        self.purge_users()

# db = Database()

# user2 = ("Anonymous", "Guest")
# user_id2 = db.create_user(user2)

# score2 = (user_id2, 17)
# db.submit_score(score2)

# user3 = ("Bob", "BobSlayer3000")
# user_id3 = db.create_user(user3)

# score3 = (user_id3, 1)
# db.submit_score(score3)

# db.purge()

# leaderboard = db.get_leaderboard()
# print(leaderboard)

# db.get_score(user_id1)

# db.get_id("Guest")