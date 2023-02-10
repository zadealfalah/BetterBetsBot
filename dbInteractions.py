from utils.py import connectDB, commandDB
#again unsure if we need to import the os, sys etc. here or if it carries over from utils.py

### user table scripts
#create a username entry into the users DB table

def createUser(username):
    connection = connectDB()
    command = commandDB(connection, "INSERT INTO users (username) VALUES ('{username}')")

# #update lastBetDate in users DB table
# def updateUserBetDate(connection, newDate, username):
#     command = commandDB(connection, "INSERT INTO users (lastBetDate) VALUES ('{newDate}') WHERE username = {username}")
#move this in to createBet()

#can use userID instead of username? unsure which is better. plenty of ways to do this one. 
#username is more human-readable maybe? but userID is technically our primary key.  both are unique though.
def updateUserBalance(balanceChange, username):
    connection = connectDB()
    command = commandDB(connection, "UPDATE users SET balance = balance + {balanceChange} WHERE username = {username}")
#keep this in case we want to manually change balances instead of just in bets

#get userBalance
def getUserBalance(username):
    connection = connectDB()
    command = commandDB(connection, "SELECT balance FROM users WHERE username = {username}")

#delete a user
def deleteUser(userID):
    connection = connectDB()
    command = commandDB(connection, "DELETE FROM users WHERE userID = {userID}")


### bets table scripts
#create bet
#maybe need to remove the 'odds'? don't remember how we wanted to update this. remove if no initial odds.
def createBet(amountBet, teamBetOn, username, gameID, odds = None):
    connection = connectDB()
    command = commandDB(connection, "INSERT INTO bets (amountBet, odds, teamBetOn, username, gameID)" +
                        "VALUES ('{amountBet}', '{odds}', '{teamBetOn}', '{username}', '{gameID}')")
    #can update user balance too.  maybe bring all our table scripts together for easier management
    #can update user last bet date here too.
    
# def updateBetOdds(newOdds, betID):
#     connection = connectDB()
#     command = commandDB(connection, "UPDATE bets SET odds = {newOdds} WHERE betID = {betID}")


def setBetResolved(connection, betID): #always happens when game winner decided, updating balance?
    command = commandDB(connection, "UPDATE bets SET resolved = 1 WHERE betID = {betID}")
    #want to update wins/losses for users too.




### game table scripts

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