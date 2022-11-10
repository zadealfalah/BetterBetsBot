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

#changed how we pull DB, should remove pullDB and re-structure
def commandDB(connection, command):
    try: 
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(command)
            connection.commit()

    except pymysql.Error as e:
        print(f"Error with pymysql: {e}")



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
def setRedditTrigger(rTrigger = "!BB"):
    trigger_phrase = rTrigger
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
    ##keep the intro/instructions though.
    selfTextStr = ""
    submission = rSub.submit(title, selftext = selfTextStr) #this submits the post with the title and EMPTY body
    submissionID = submission.id #get submissionID

    connection = connectDB()
    for index, row in df.iterrows():
        selfTextStr = selfTextStr + f"{row['teamNameZero']} vs. {row['teamNameOne']} on {row['gameStartTime'].strftime('%A')} \n"
        command = commandDB(connection, f"INSERT INTO games (postID, gameID) VALUES ({submissionID}, {row['gameID']})") 

    #may need sleep here to adress timeout error? see if so.
    submission.edit(selftext = selfTextStr) #edit so that we can get submissionID earlier for entry into DB


#we want the submissionID created once we submit the post above, unsure the best way to do this. 
#does rSub.submit(title, selftext = selfTextStr) exist as a submission object now? if so can just do: postID = rSub.submit(title, selftext = selfTextStr).id
# #seems to be the case according to: https://www.reddit.com/r/redditdev/comments/m5ap3b/whats_the_best_way_to_get_an_id_of_a_post_ive/


#this requires we import from betsScripts.py
#betScripts.py imports from utils.py (which is this script)
#may want to separate utils.py into utils.py and redditUtils.py or something
#keeping for now
from betsScripts.py import createBet

def scanRedditPost(postIDToScan, trigger = setRedditTrigger(), rInstance = createReddit()):
    connection = connectDB() #connect to db
    submission = rInstance.submission(postIDToScan) #get the post submission object
    commandString = f"SELECT commentID FROM messageLog WHERE postID = {postIDToScan}" ####This relies on messageLog table working as intended, double check!
    df = pd.read_sql(commandString, connection)  #use df to see comments already logged within a post

    betsToMake = {} #store all bets to make here
    balancesToCheck = {} #store all balances to check here
    winsToCheck = {} #store all wins to check here
    topToPost = {} #store all the people we need to report the top5 to
    unrecognizedToPost = {} #store all people we need to report unrecognized commands to

    #we will look only at top-level comments here.  can change to look at deeper comments later
    for tComment in submission.comments: #tComment for a top-level-comment
        if trigger not in tComment: #trigger not in tComment, continue
            continue
        elif isinstance(tComment, MoreComments): #if it's a 'more comments' link, just keep on going
            continue
        elif tComment.id in df.commentID: #comment already logged in our table
            continue
        else: #trigger is in the comment, it's not a 'more comment', we haven't logged it yet, so we're good to go
            cComm = tComment.body.split(trigger) #split on the trigger so as to get rid of anything before it, call it cComm for currentComment, keep tComment (original) in case we need for now
            splitComm = cComm.strip().lower().split() #now it's a list of the words
            actionTaken = splitComm[0] #action the user wants to take e.g. BET, BALANCE, WINS, TOP5
            #could remove above line and just go with cComm[0] but keeping because I keep forgetting for now.

            #work through the case where actionTaken == BET first
            #right now user tComment.id as key, could switch and use userID or username as key
            #if we switch, be sure to add userID (tComment.author.id) as key AND 
            #be sure to add tComment.id within e.g. via 
            #betsToMake[tComment.author.id]['commentID'] = tComment.id
            if actionTaken.lower() == 'bet':
                betsToMake[tComment.id] = {}
                betsToMake[tComment.id]['username'] = tComment.author.name #reddit username of comment poster
                betsToMake[tComment.id]['amountBet'] = splitComm[1]
                betsToMake[tComment.id]['teamNameZero'] = splitComm[2] #currently req. full name, should allow for aliases/shortening imo later
                betsToMake[tComment.id]['dayOfWeek'] = splitComm[3]

            #now if actionTaken == BALANCE  
            elif actionTaken.lower() == 'balance':
                balancesToCheck[tComment.id] = {}
                balancesToCheck[tComment.id]['username'] = tComment.author.name #reddit username of commnet poster
            
            #now if actionTaken == WINS
            elif actionTaken.lower() == 'wins':
                winsToCheck[tComment.id] = {}
                winsToCheck[tComment.id]['username'] = tComment.author.name #reddit username of comment poster

            #now if actionTaken == TOP5
            elif actionTaken.lower() == 'top5':
                topToPost[tComment.id] = {}
                topToPost[tComment.id]['username'] = tComment.author.name #reddit username of comment poster

            else: #actionTaken is not recognized
                unrecognizedToPost[tComment.id] = {}
                unrecognizedToPost[tComment.id]['username'] = tComment.author.name #reddit username of comment poster

            #finally here once we check all cases, add the comment to messageLog
            ##messageLog not operational yet, should check this once it is!
            command = commandDB(connection, f"""INSERT INTO messageLog (commentID, truncBody, commandGiven, respondedTo, postID, username)
                                            VALUES ({tComment.id}, {cComm[:50]}, {actionTaken}, 1, {tComment.id}, {tComment.author.name})""")
                                ##Do these VALUES need apostrophes around them?
    return betsToMake, balancesToCheck, winsToCheck, topToPost, unrecognizedToPost
    #returns the dictionaries as they are at the end of this, can deal with empty ones once we call from them
            

longtest = "this is a long test string with many characters aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
print(len(longtest))
longtest[:50]

testdict = {}
testdict['testkey'] = 'testval'
print(len(testdict))

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


#function to find calls to bot in inbox
#have 'testing' arg to search only through 10 things in inbox, save computation. default to TRUE for now.
#splits the call into actions and returns 

#have it look through threads we create for the trigger phrase
#add postID to games database for reference

# def getRedditAction(redditInstance, trigger_phrase = setRedditTrigger(), testing = True):
#     storageDict = {} #to store message details as needed
#     for item in redditInstance.inbox.all(limit=10):
#         print(repr(item))
#     if testing == True:
#         print("Testing Mode ON!")
#         inbox_to_search = redditInstance.inbox.all(limit = 10) #if testing, look through 10 entries in inbox
#     else:
#         inbox_to_search = redditInstance.inbox.all(limit = None) #unlimited number of entries if not testing
#     print("Got to here")
#     for message in inbox_to_search:
#         print("Got to message")
#         if trigger_phrase in message.body:
#             cList = message.body.split() #turn message body into comment list called cList
#             print(cList) #testing

#             # storageDict[message.author.name] = {} #create nested dict with author username as keyword
#             # storageDict[message.author.name]['action'] = cList[1] #add action from message to nested dict
#             # storageDict[message.author.name]['timePosted'] = message.created_utc #add utc creation time of message


#         else:
#             continue

#         # message.mark_read() #mark the message as read




