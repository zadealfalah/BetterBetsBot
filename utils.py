import os
from dotenv import load_dotenv
import pymysql.cursors
import sys
import praw
from datetime import datetime #used only in creating reddit post right now, may want to move this import?
import pandas as pd
load_dotenv()


#function to connect to DB via .env file credentials
#uses DictCursor
#returns 'connection' object
def connectDB():
    connection = pymysql.connect(host=os.getenv('db_host'),
                                user=os.getenv('db_user'),
                                password=os.getenv('db_pass'),
                                database=os.getenv('db_schema'),
                                cursorclass=pymysql.cursors.DictCursor)
    return connection


#function to issue commands, takes in the command itself and a connection object
#e.g command: "INSERT INTO users (username) VALUES ("testname")
#above command inserts a user


##changing this, using pd.read_sql for reading
#changed how we pull DB, should remove pullDB and re-structure
def commandDB(connection, command):
    try: 
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(command)
            connection.commit()

    except pymysql.Error as e:
        print(f"Error with pymysql: {e}")



#e.g. key_list: ["username", "bet_amount", "gameBetOn"] #list of columns to be inserted into
#e.g. values_dict: {"username" ["Zade", "Jonny", "Cat"], "bet_amount"}

#may want to keep reddit creation in here or maybe make a 'redditScripts.py' or something, can consider. leave here for now.
#function to create reddit instance
#returns reddit instance
def createReddit():
    reddit = praw.Reddit(client_id = os.getenv('red_client_id'),
                     client_secret = os.getenv('red_client_secret'),
                     username = os.getenv('red_user'),
                     password = os.getenv('red_password'),
                     user_agent = os.getenv('red_user_agent'))
    return reddit

#set the sub we're pulling from for our reddit instance, default to 'test'
#returns the reddit.subreddit instance
def setRedditSub(rInstance, rSub = 'test'):
    target_sub = rSub
    subreddit = rInstance.subreddit(target_sub)
    return subreddit

#function to set reddit trigger phrase
#probably won't change, but may as well have in case we do e.g. !BBB or something, won't have to change them all
#returns the trigger phrase
rTrigger = "!BB" #global as we use it in responses, easier to change
def setRedditTrigger(currentTrigger = rTrigger):
    trigger_phrase = currentTrigger
    return trigger_phrase


#pull games as follows:
#get current time when this is ran to get start time, add 7 days to this to get end time, pull all games from games table within this timeframe
#the weekStartTime is from a NOW() command that runs when the code is ran, can set in pythonanywhere to run at start of week to automate
#returns df with the requisite rows from the games table
#be sure of when we start the run on pythonanywhere, weeks are set in weird spots (not starting on Sunday)
def getGamesOfWeek(league, weekStartTime):
    connection = connectDB()
    commandString = f"SELECT * FROM games WHERE gameStartTime > NOW() AND gameStartTime < NOW() + INTERVAL 1 WEEK"
    df = pd.read_sql(commandString, connection, index_col = 'gameID')
    return df



#function to create the reddit post
#df from getGamesOfWeek(league, weekStartTime)
def createRedditPost(df, weekNumber, rSub = setRedditSub(createReddit())):
    leagueName = df.league[0] #any of the leagues should work as the df was selected with the league in getGamesOfWeek()
    title = f"Better Bets Week {weekNumber} {leagueName} Post" #e.g. Better Bets Week 5 NFL Post

    ##Should make this first string an intro/instruction, end it with something like:
    ##"Loading Games, Refresh for Edits" which would be removed once we add games
    ##keep the intro/instructions though. NOTE IN RULES ONLY TOP LEVEL COMMENTS
    selfTextStr = ""
    submission = rSub.submit(title, selftext = selfTextStr) #this submits the post with the title and EMPTY body
    submissionID = submission.id #get submissionID

    connection = connectDB()
    for index, row in df.iterrows():
        selfTextStr = selfTextStr + f"{row['teamNameZero']} vs. {row['teamNameOne']} on {row['gameStartTime'].strftime('%A')} \n"
        command = commandDB(connection, f"INSERT INTO games (postID, gameID) VALUES ({submissionID}, {row['gameID']})") 

    #may need sleep here to adress timeout error? see if so.
    submission.edit(selftext = selfTextStr) #edit so that we can get submissionID earlier for entry into DB
##may want to return postID here

#we want the submissionID created once we submit the post above, unsure the best way to do this. 
#does rSub.submit(title, selftext = selfTextStr) exist as a submission object now? if so can just do: postID = rSub.submit(title, selftext = selfTextStr).id
# #seems to be the case according to: https://www.reddit.com/r/redditdev/comments/m5ap3b/whats_the_best_way_to_get_an_id_of_a_post_ive/


#this requires we import from betsScripts.py
#betScripts.py imports from utils.py (which is this script)
#may want to separate utils.py into utils.py and redditUtils.py or something
#keeping for now
from betsScripts import createBet
from praw.models import MoreComments #required for comment selection
from usersScripts import getUserBalance

#returns 5 dictionaries in order of bets, balances, wins, top5, unrecognized



##changed responses, must change scan. 
#ADD !BB HELP
def scanRedditPost(postIDToScan, trigger = setRedditTrigger(), rInstance = createReddit()):
    connection = connectDB() #connect to db
    submission = rInstance.submission(postIDToScan) #get the post submission object
    commandString = f"SELECT commentID FROM messageLog WHERE postID = {postIDToScan}" ####This relies on messageLog table working as intended, double check!
    alreadySeen_df = pd.read_sql(commandString, connection)  #use df to see comments already logged within a post
    connection.close()

    #we will look only at top-level comments here.  can change to look at deeper comments later
    for tComment in submission.comments: #tComment for a top-level-comment
        if trigger not in tComment: #trigger not in tComment, continue
            continue
        elif isinstance(tComment, MoreComments): #if it's a 'more comments' link, just keep on going
            continue
        elif tComment.id in alreadySeen_df.commentID: #comment already logged in our table
            continue
        else: #trigger is in the comment, it's not a 'more comment', we haven't logged it yet, so we're good to go
            cComm = tComment.body.split(trigger)[1] #split on the trigger so as to get rid of anything before it, call it cComm for currentComment, keep tComment (original) in case we need for now
            splitComm = cComm.strip().lower().split() #now it's a list of the words
            actionTaken = splitComm[0] #action the user wants to take e.g. BET, BALANCE, WINS, TOP5
            connection = connectDB()
            command = commandDB(connection, f"""INSERT INTO messageLog (commentID, truncBody, commandGiven, respondedTo, postID, username)
                                            VALUES ({tComment.id}, {cComm[:50]}, {actionTaken}, 0, {postIDToScan}, {tComment.author.name})""")
                                ##Do these VALUES need apostrophes around them?

##For all reads, do pd.read_sql()


#craft the responses to our stored actions from a scanRedditPost() command
#remember that those stored actions are kept in the messageLog db table
def respondReddit(): #could change to have postID to call only on specific posts. not needed for now.

    connection = connectDB() #connect to db
    commandString = f"SELECT * FROM messageLog WHERE respondedTo = 0" ####This relies on messageLog table working as intended, double check!
    unseenDF = pd.read_sql(commandString, connection)  #use df to see comments not yet responded to
    #read_sql seems to only close the cursor, not the connection.  Lets try to close it manually
    connection.close() #things like createBet() make their own connection, don't want multiple.
    
    #avoid remaking top5 dataframe every time by making it here iff 'top5' was asked for 1 or more times
    if unseenDF.commandGiven.isin(['top5']):
        connection = connectDB()
        commandString = f"SELECT username, balance FROM users ORDER BY balance DESC LIMIT 5"
        top5DF = pd.read_sql(commandString, connection)
        connection.close()

    for index, row in unseenDF.iterrows():
        #First go through unseen bets
        if row['commandGiven'] == 'bet':
            #if it's a bet, we want to add a bet to the bets table
            splitComm = row['truncBody'].strip().lower().split() #turn body text into list of the words
            amountBet = splitComm[1]
            teamBetOn = splitComm[2].lower() #will need to better normalize team names
            dayOfWeek = splitComm[3] if len(splitComm) > 3 else "" #make it so dayOfWeek is optional
            createBet(amountBet, teamBetOn, row['userID'], row['gameID']) #create the bet
            ##must update createBet to update user balance automatically!
            ##also update createBet to automatically update users' last bet date

            #respond and let them know the bet was set
            comment = rInstance.comment(row['commentID'])
            comment.reply(f"Your bet of {amountBet} for {teamBetOn} has been added!")

        elif row['commandGiven'] == 'balance':
            userCurrentBalance = getUserBalance()
            comment = rInstance.comment(row['commentID'])
            comment.reply(f"Your current balance is {userCurrentBalance}")

        elif row['commandGiven'] == 'winloss':
            #if it's winloss, we want to respond with the users' current winloss
            connection = connectDB()
            commandString = f"SELECT nWins, nLosses, nWins/nLosses as wlr FROM users WHERE username = {row['userID']}"
            wlrDF = pd.read_sql(commandString, connection)
            connection.close()
            #respond with stats for the user
            comment = rInstance.comment(row['commentID'])
            comment.reply(f"Your current win/loss ratio is: {round(wlrDF.wlr,3)} with {wlrDF.nWins} wins and {wlrDF.nLosses} losses.")

        elif row['commandGiven'] == 'top5':
            #could have top5 in either WL or balance. for now assume balance is what we want
            #top5DF table was made earlier iff there was one or more top5 responses to be given
            #now respond to the person that asked with the relevant details
            comment = rInstance.comment(row['commentID'])
            comment.reply(f"""The current top 5 users by balance are: \n
               """) #read through and respond w/ top5 username / balance.  how to format response nicely?
               #in either case we respond with rows from the top5DF. just figure out how to format for reddit

        elif row['commandGiven'] == 'help':
            comment = rInstance.comment(row['commentID'])
            comment.reply(f"""Currently supported commands are: 'bet', 'balance', 'winloss', 'top5', and 'help'. \n
            For example you may type '{rTrigger} BET 500 Lions' to bet 500 on the Lions game in this weeks' post. \n
            Other commands need only the trigger and the phrase e.g. '{rTrigger} BALANCE'.  Capitalization does not matter.""")
        else: #the command given was invalid
            #if the command was invalid, we want to respond letting them know that it was invalid
            comment = rInstance.comment(row['commentID'])
            comment.reply(f"Unfortunately your command was not understood.  Please try {rTrigger} HELP")



longtest = "this is a long test string with many characters aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
print(len(longtest))
longtest[:50]

testbet = {}
testbet['test1'] = {'username': 'testname1'}
testbet['test2'] = {'username': 'testname2'}
templist = [x.get('username') for x in list(testbet.values()) if x.get('username')]
print(templist)

#example message body for testing:
#   !BB BET 100 PACKERS SUNDAY
#so we assume for all this that cList[0] is the call to the bot
#cList[1] is the action to be taken
#cList[2:] depends on action to be taken? may be a way to formalize structure. should talk about it.


teststr = """Lets try this then \n
"!BB BET 100 PACKERS SUNDAY"""
print(teststr)
print(teststr.split("!BB")[1])
testcurrent = teststr.split("!BB")[1]
print(testcurrent.strip().lower().split())

if "!bb" not in teststr.lower():
    print("!bb is NOT in here")
else:
    print("Yep!")







def insertQueryConstructor(tableToInsert, columnsToInsert, valuesToInsert):

    """
    action - 
    table -
    key_list - ["username". "bet_amount", "gameBetOn"] (This a list of columns to be inserted )
    tuple_list = [(zade, 100, 45), (jonny, 50, 43), (cat, 4000, 43)]
    """

    commandGiven = F"INSERT INTO {table} ({','.join(key_list)}) VALUES "

    for tup in tuple_list:

        string = F"({','.join(str(x) for x in tup)}),"
        commandGiven += string

    commandGiven = commandGiven.rstrip(",")

    return commandGiven

#testing below
# if __name__ == "__main__":
#    command = insertQueryHelper("bets", ["username", "bet_amount", "gameBetOn"], [('zade', 100, 45), ('jonny', 50, 43), ('cat', 4000, 43)])
#    print (command)





#when game over, look at all bets that aren't resolved that have same game number
#fill in odds with UPDATE CASE command
#take that to create new var of odds*amountBet (call it resolvedBetAmount or something)
#join games to bets to users, update balance with resolvedBetAmount


def gamefinished()