from utils import connectDB, commandDB
#again unsure if we need to import the os, sys etc. here or if it carries over from utils.py


#create bet
#maybe need to remove the 'odds'? don't remember how we wanted to update this. remove if no initial odds.
def createBet(amountBet, teamBetOn, username, gameID, odds = None):
    connection = connectDB()
    command = commandDB(connection, "INSERT INTO bets (amountBet, odds, teamBetOn, username, gameID)" +
                        "VALUES ('{amountBet}', '{odds}', '{teamBetOn}', '{username}', '{gameID}')")


# def updateBetOdds(newOdds, betID):
#     connection = connectDB()
#     command = commandDB(connection, "UPDATE bets SET odds = {newOdds} WHERE betID = {betID}")


def setBetResolved(connection, betID): #always happens when game winner decided, updating balance?
    command = commandDB(connection, "UPDATE bets SET resolved = 1 WHERE betID = {betID}")


