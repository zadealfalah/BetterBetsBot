from utils.py import connectDB, commandDB
#again unsure if we need to import the os, sys etc. here or if it carries over from utils.py


#create a game entry
def createGame(teamNameZero, gameStartTime, league, teamNameOne):
    connection = connectDB()
    command = commandDB(connection, "INSERT INTO games (teamNameZero, gameStartTime, league, teamNameOne)" +
                        "VALUES ('{teamNameZero}', '{gameStartTime}', '{league}', '{teamNameOne}'")




#set game winner to 0 or 1 for 1st or 2nd listed team winning respectively
def setGameWinner(teamWon, gameID):
    connection = connectDB()
    command = commandDB(connection, "UPDATE games SET winner = {teamwon} WHERE gameID = {gameID}")



#delete old game
def deleteGame(gameID):
    connection = connectDB()
    command = commandDB(connection, "DELETE FROM games WHERE gameID = {gameID}")