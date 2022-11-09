from utils.py import connectDB, commandDB
#again unsure if we need to import the os, sys etc. here or if it carries over from utils.py

#set game winner to 0 or 1 for 1st or 2nd listed team winning respectively
def setGameWinner(teamWon, gameID):
    connection = connectDB()
    command = commandDB(connection, "UPDATE games SET winner = {teamwon} WHERE gameID = {gameID}")


