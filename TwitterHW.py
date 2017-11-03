# Import statements
import unittest
import sqlite3
import requests
import json
import re
import tweepy
import twitter_info # still need this in the same directory, filled out

consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and return it in a JSON format
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser()) #api to access twitter

# And we've provided the setup for your cache. But we haven't written any functions for you, so you have to be sure that any function that gets data from the internet relies on caching.
CACHE_FNAME = "twitter_cache.json" #naming cache file
try:
    cache_file = open(CACHE_FNAME,'r') #opening a file 
    cache_contents = cache_file.read() #reading a file
    cache_file.close() #close file
    CACHE_DICTION = json.loads(cache_contents) #loading contents of file
except:
    CACHE_DICTION = {} #dictionary

## [PART 1]

# Here, define a function called get_tweets that searches for all tweets referring to or by "umsi"
# Your function must cache data it retrieves and rely on a cache file!


def get_tweets():
    if 'umsi' in CACHE_DICTION: #if umsi is in the cache
        print('using cache... ') #print the phrase
        search_results = CACHE_DICTION['umsi'] #variable indexing the search umsi in cache
    else:
        print('fetching data... ') #print the phrase
        search_results = api.user_timeline('umsi') #search for umsi on twitter

        CACHE_DICTION['umsi'] = search_results #adding to cache
        wfile= open(CACHE_FNAME, 'w') #opening cache
        wfile.write(json.dumps(CACHE_DICTION)) #writing the dictionary/ loading it
        wfile.close() #closing cache

    return search_results #return the search results


## [PART 2]
# Create a database: tweets.sqlite,
# And then load all of those tweets you got from Twitter into a database table called Tweets, with the following columns in each row:
## tweet_id - containing the unique id that belongs to each tweet
## author - containing the screen name of the user who posted the tweet (note that even for RT'd tweets, it will be the person whose timeline it is)
## time_posted - containing the date/time value that represents when the tweet was posted (note that this should be a TIMESTAMP column data type!)
## tweet_text - containing the text that goes with that tweet
## retweets - containing the number that represents how many times the tweet has been retweeted

# Below we have provided interim outline suggestions for what to do, sequentially, in comments.

# 1 - Make a connection to a new database tweets.sqlite, and create a variable to hold the database cursor.
conn =sqlite3.connect('tweets.db') #creating the sql database
cur = conn.cursor() #creating variable to hold the database cursor

# 2 - Write code to drop the Tweets table if it exists, and create the table (so you can run the program over and over), with the correct (4) column names and appropriate types for each.
# HINT: Remember that the time_posted column should be the TIMESTAMP data type!
cur.execute('DROP TABLE IF EXISTS Tweets')
cur.execute('CREATE TABLE Tweets (tweet_id TEXT, author TEXT, time_posted TIMESTAMP, tweet_text TEXT, retweets NUMBER)') #making columns and rows for table

# 3 - Invoke the function you defined above to get a list that represents a bunch of tweets from the UMSI timeline. Save those tweets in a variable called umsi_tweets.
umsi_tweets = get_tweets() #invoking the function

# 4 - Use a for loop, the cursor you defined above to execute INSERT statements, that insert the data from each of the tweets in umsi_tweets into the correct columns in each row of the Tweets database table.

for tw in umsi_tweets: #looking for tweet in the function
    tup = tw["id"], tw["user"]["screen_name"], tw["created_at"], tw["text"], tw["retweet_count"] #creating tuple pairs
    cur.execute('INSERT INTO Tweets (tweet_id, author, time_posted, tweet_text, retweets) VALUES (?, ?, ?, ?, ?)', tup) #inserting tuples into table

#  5- Use the database connection to commit the changes to the database
conn.commit() #committing database changes
# You can check out whether it worked in the SQLite browser! (And with the tests.)

## [PART 3] - SQL statements
# Select all of the tweets (the full rows/tuples of information) from umsi_tweets and display the date and message of each tweet in the form:
    # Mon Oct 09 16:02:03 +0000 2017 - #MondayMotivation https://t.co/vLbZpH390b
    #
    # Mon Oct 09 15:45:45 +0000 2017 - RT @MikeRothCom: Beautiful morning at @UMich - It’s easy to forget to
    # take in the view while running from place to place @umichDLHS  @umich…
# Include the blank line between each tweet.
print("tests for part 3") 
cur.execute("SELECT time_posted, tweet_text FROM Tweets") #seelction tweets from umsi tweets
all_res = cur.fetchall() #fetching tweets
for t in all_res: 
    print(t[0] + " - " + t[1] + "\n") #printing the tweets and when they were written

# Select the author of all of the tweets (the full rows/tuples of information) that have been retweeted MORE
# than 2 times, and fetch them into the variable more_than_2_rts.
# Print the results
cur.execute("SELECT author FROM Tweets WHERE retweets>2") #selecting author of tweets that have been retweeted 2 times
more_than_2_rts = cur.fetchall() #fetching data
print("more_than_2_rts - %s" %set(more_than_2_rts)) #printing the name of whats been retweeted more than 2 times

cur.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
