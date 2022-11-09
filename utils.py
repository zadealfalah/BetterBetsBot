import os
from dotenv import load_dotenv
import pymysql.cursors
import sys
import praw
load_dotenv()

#do we need these imports on every single script? or just on one that will run first to connect to db?

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
def commandDB(connection, command):
    with connection:
        with connection.cursor() as cursor:
            sql = f"{command}"
            cursor.execute(sql)
        connection.commit()

    #do we then issue a bash command here? leaving as-is for now



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
def setRedditSub(redditInstance, sub = 'test'):
    target_sub = sub
    subreddit = reddit.subreddit(target_sub)
    return subreddit

#function to set reddit trigger phrase
#probably won't change, but may as well have in case we do e.g. !BBB or something, won't have to change them all
#returns the trigger phrase
def setRedditTrigger(trigger = "!BB"):
    trigger_phrase = trigger
    return trigger_phrase


#function to find calls to bot in inbox
#have 'testing' arg to search only through 10 things in inbox, save computation. default to TRUE for now.
#splits the call into actions and returns 

#right now looks through inbox, could change so we have something look for mentions in subreddits. should talk about.
#looks through whole inbox, change to look only at unread and setting settled ones to read later.
def getRedditAction(redditInstance, trigger_phrase = setRedditTrigger(), testing = True):
    storageDict = {} #to store message details as needed
    for item in redditInstance.inbox.all(limit=10):
        print(repr(item))
    if testing == True:
        print("Testing Mode ON!")
        inbox_to_search = redditInstance.inbox.all(limit = 10) #if testing, look through 10 entries in inbox
    else:
        inbox_to_search = redditInstance.inbox.all(limit = None) #unlimited number of entries if not testing
    print("Got to here")
    for message in inbox_to_search:
        print("Got to message")
        if trigger_phrase in message.body:
            cList = message.body.split() #turn message body into comment list called cList
            print(cList) #testing

            # storageDict[message.author.name] = {} #create nested dict with author username as keyword
            # storageDict[message.author.name]['action'] = cList[1] #add action from message to nested dict
            # storageDict[message.author.name]['timePosted'] = message.created_utc #add utc creation time of message


        else:
            continue

        # message.mark_read() #mark the message as read




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

print(os.getenv('red_client_id'))
print(os.getenv('red_client_secret'))
print(os.getenv('red_user'))
print(os.getenv('red_password'))
print(os.getenv('red_user_agent'))