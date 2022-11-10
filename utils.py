import os
from dotenv import load_dotenv
import pymysql.cursors
import sys
import praw
from datetime import datetime #used only in creating reddit post right now, may want to move this import?
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
def getGamesOfWeek(league, weekStartTime):
    connection = connectDB()
    commandString = f"SELECT * FROM games WHERE gameStartTime > NOW() AND gameStartTime < NOW() + INTERVAL 1 WEEK"
    df = pd.read_sql(commandString, connection, index_col = 'gameID')
    return df



#function to create the reddit post
#df from getGamesOfWeek(league, weekStartTime)
def createRedditPost(rSub = setRedditSub(), df, weekNumber):
    leagueName = df.league[0] #any of the leagues should work as the df was selected with the league in getGamesOfWeek()
    title = f"Better Bets Week {weekNumber} {leagueName} Post" #e.g. Better Bets Week 5 NFL Post

    selfTextStr = ""


    for index, row in df.iterrows():
        selfTextStr = selfTextStr + f"{row['teamNameZero']} vs. {row['teamNameOne']} on {row['gameStartTime'].strftime('%A')} \n"
        
    submission = rSub.submit(title, selftext = selfTextStr) #this submits the post with the title and body (self) text

    #we want the submissionID created once we submit the post above, unsure the best way to do this. 
    #does rSub.submit(title, selftext = selfTextStr) exist as a submission object now? if so can just do: postID = rSub.submit(title, selftext = selfTextStr).id
    #seems to be the case according to: https://www.reddit.com/r/redditdev/comments/m5ap3b/whats_the_best_way_to_get_an_id_of_a_post_ive/
    submissionID = submission.id


    #must now add the post and games to the gamePost table
    #can't do it in original iterrows() since the post wasn't created yet. may be a better way to organize this
    connection = connectDB()
    for index, row in df.iterrows():
        command = commandDB(connection, f"INSERT INTO gamePost (postID, gameID) VALUES ({submissionID}, {row['gameID']})")







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




#example message body for testing:
#   !BB BET 100 PACKERS SUNDAY
#so we assume for all this that cList[0] is the call to the bot
#cList[1] is the action to be taken
#cList[2:] depends on action to be taken? may be a way to formalize structure. should talk about it.

testcom = "!BBB BET 100 PACKERS SUNDAY"
print(testcom.split())
print(testcom.split()[1])


red_Inst = createReddit()

getRedditAction(redditInstance = red_Inst, trigger_phrase = 'testing')

list(red_Inst.inbox.all())
