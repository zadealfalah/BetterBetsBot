from utils.py import connectDB, commandDB
#again unsure if we need to import the os, sys etc. here or if it carries over from utils.py


#create a username entry into the users DB table
def createUser(username):
    connection = connectDB()
    command = commandDB(connection, "INSERT INTO users (username) VALUES ('{username}')")

#update lastBetDate in users DB table
def updateUserBetDate(connection, newDate, username):
    command = commandDB(connection, "INSERT INTO users (lastBetDate) VALUES ('{newDate}') WHERE username = {username}")

#can use userID instead of username? unsure which is better. plenty of ways to do this one. 
#username is more human-readable maybe? but userID is technically our primary key.  both are unique though.
def updateUserBalance(connection, balanceChange, username):
    command = commandDB(connection, "UPDATE users SET balance = balance + {balanceChange} WHERE username = {username}")


#get userBalance
def getUserBalance(username):
    connection = connectDB()
    command = commandDB(connection, "SELECT balance FROM users WHERE username = {username}")

#delete a user
def deleteUser(userID):
    connection = connectDB()
    command = commandDB(connection, "DELETE FROM users WHERE userID = {userID}")