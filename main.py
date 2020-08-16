import configparser
import tweepy
from random import randint
import sched
import time

class main:

    config = None
    auth = None
    twitterAPI = None
    words = None
    symbols = None
    scheduler = None
    delay = 1
    hashtag = False

    def __init__(self):

        # Open and prepare the configuration
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        # Connect to the Twitter API through the Tweepy library
        self.auth = tweepy.OAuthHandler(self.config["Auth"]["APIKey"],self.config["Auth"]["APISecret"])
        self.auth.set_access_token(self.config["Auth"]["AccessToken"],self.config["Auth"]["AccessTokenSecret"])
        self.twitterAPI = tweepy.API(self.auth)

        # Check if we are hashtagging
        if self.config["Configuration"]["hashtag"].upper() == "TRUE":
            self.hashtag = True


        # Turn symbols to a list
        self.symbols = [char for char in self.config["Configuration"]["symbolsToUse"]]

        # Create the task scheduling
        self.scheduler = sched.scheduler(time.time, time.sleep)

        # Get the scheduler delay time
        self.delay = (float(self.config["Configuration"]["intervalHours"])*60)*60

        # Check the credentials are correct
        try:
            self.twitterAPI.verify_credentials()
            print("Authentication Passed")
        except:
            print("Authentication Failed")
            exit()

        # Open the 10000 Word Document
        with open(self.config["Configuration"]["wordFile"], "r") as file:
            self.words = file.readlines()

        # Set up the scheduler so the task is run within scheduled time slots defined by the delay value in the config
        self.scheduler.enter(0,1,self.post)
        self.scheduler.run()

    def post(self):

        # Get the symbol to use
        symbol = self.symbols[randint(0,len(self.symbols)-1)]

        # Get the two words
        num1 = randint(0, len(self.words)-1)
        word1 = self.words[num1]

        # Verify the same numbers were not chosen
        num2 = randint(0, len(self.words)-1)
        while (num1 == num2):
            num2 = randint(0, len(self.words)-1)
        word2 = self.words[num2]

        # Capitalise the beginning of both words and remove the line breaks
        word1, word2 = word1.title().rstrip(), word2.title().rstrip()

        # Post the statement to twitter
        if self.hashtag:
            self.twitterAPI.update_status("#"+word1 + " " + symbol + " " + "#"+word2)
        else:
            self.twitterAPI.update_status(word1 + " " + symbol + " " + word2)

        # Re enter the scheduler
        self.scheduler.enter(self.delay,1,self.post)

if __name__ == "__main__":
    main()

