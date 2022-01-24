import json
import random
import datetime

print("\033c")

def createUser(username):

    with open("data/data.json", "r") as openfile:
        currentDataFile = json.load(openfile)

    dictionary = {
        "dateCreated" : datetime.datetime.now().strftime("%x"),
        "timeCreated" : datetime.datetime.now().strftime("%X"),
        "easy" : { 
            "bestTime" : 999,
            "bestTime_Date" : None,   
            "bestTime_Time" : None   
            },
        "medium" : { 
            "bestTime" : 999,
            "bestTime_Date" : None,   
            "bestTime_Time" : None   
            },
        "hard" : { 
            "bestTime" : 999,
            "bestTime_Date" : None,   
            "bestTime_Time" : None   
            }
        }
    
    currentDataFile[username] = dictionary
    jsonObject = json.dumps(currentDataFile, indent = 4)

    with open("data/data.json", "w") as outfile:
        outfile.write(jsonObject)


class save():
    def __init__(self, username):
        self.username = username
        self.date = datetime.datetime.now().strftime("%x")
        self.time = datetime.datetime.now().strftime("%X")
        
        with open("data/data.json", "r") as openfile:
            currentDataFile = json.load(openfile)

        if not (username in currentDataFile):
            createUser(self.username)

        with open("data/data.json", "r") as openfile:
            self.dataFile = json.load(openfile)

    def score(self, difficulty, score):
        if self.dataFile[self.username][difficulty]["bestTime"] <= score:
            pass
        else:
            self.dataFile[self.username][difficulty]["bestTime"] = score
            self.dataFile[self.username][difficulty]["bestTime_Date"] = self.date
            self.dataFile[self.username][difficulty]["bestTime_Time"] = self.time
            jsonObject = json.dumps(self.dataFile, indent = 4)
            with open("data/data.json", "w") as outfile:
                outfile.write(jsonObject)


class leaderboard():
    def __init__(self):
        with open("data/data.json", "r") as openfile:
            self.dataFile = json.load(openfile)

    def bestScores(self, difficulty):
        username = min(self.dataFile.items(), key=lambda v: int(self.dataFile[v[0]][difficulty]['bestTime']))[0]
        bestScore = min(self.dataFile.items(), key=lambda v: int(self.dataFile[v[0]][difficulty]['bestTime']))[1][difficulty]["bestTime"]
        bestScoreDate = min(self.dataFile.items(), key=lambda v: int(self.dataFile[v[0]][difficulty]['bestTime']))[1][difficulty]["bestTime_Date"]
        bestScoreTime = min(self.dataFile.items(), key=lambda v: int(self.dataFile[v[0]][difficulty]['bestTime']))[1][difficulty]["bestTime_Time"]
        return username, bestScore, bestScoreDate, bestScoreTime