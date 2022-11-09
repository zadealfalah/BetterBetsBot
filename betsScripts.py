from utils.py import connectDB, commandDB
#again unsure if we need to import the os, sys etc. here or if it carries over from utils.py


#create bet
#maybe need to remove the 'odds'? don't remember how we wanted to update this. remove if no initial odds.
def createBet(amountBet, odds = None, teamBetOn, userID, gameID):
    connection = connectDB()
    command = commandDB(connection, "INSERT INTO bets (amountBet, odds, teamBetOn, userID, gameID)" +
                        "VALUES ('{amountBet}, '{odds}', '{teamBetOn}', '{userID}', '{gameID}')")


def updateBetOdds(newOdds, betID):
    connection = connectDB()
    command = commandDB(connection, "UPDATE bets SET odds = {newOdds} WHERE betID = {betID}")


def setBetResolved(connection, betID): #always happens when game winner decided, updating balance?
    command = commandDB(connection, "UPDATE bets SET resolved = 1 WHERE betID = {betID}")


