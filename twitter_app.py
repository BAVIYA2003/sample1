import time
import tweepy
from threading import Thread
import os
from os.path import join, dirname
from dotenv import Dotenv


import operator
# from Queue.Queue import Queue

from Queue import Queue
# import get_all_tweets
dotenv_path = join(dirname(__file__), 'env')
dotenv = Dotenv(dotenv_path)
os.environ.update(dotenv)
# load_dotenv(dotenv_path)

tweets_time = []
count = 0
consumer_token = os.environ.get("CONSUMER_TOKEN")
consumer_secret = os.environ.get("CONSUMER_SECRET")

key = os.environ.get("ACCESS_TOKEN")
secret = os.environ.get("ACCESS_KEY")

auth = tweepy.OAuthHandler(consumer_token, consumer_secret)

auth.set_access_token(key, secret)
api = tweepy.API(auth)

hour_dict = {0:"12:00 AM - 1:00 AM",
             1:"1:00 AM - 2:00 AM",
             2:"2:00 AM - 3:00 AM",
             3:"3:00 AM - 4:00 AM",
             4:"4:00 AM - 5:00 AM",
             5:"5:00 AM - 6:00 AM",
             6:"6:00 AM - 7:00 AM",
             7:"7:00 AM - 8:00 AM",
             8:"8:00 AM - 9:00 AM",
             9:"9:00 AM - 10:00 AM",
             10:"10:00 AM - 11:00 AM",
             11:"11:00 AM - 12:00 AM",
             12:"12:00 PM - 1:00 PM",
             13:"1:00 PM - 2:00 PM",
             14:"2:00 PM - 3:00 PM",
             15:"3:00 PM - 4:00 PM",
             16:"4:00 PM - 5:00 PM",
             17:"5:00 PM - 6:00 PM",
             18:"6:00 PM - 7:00 PM",
             19:"7:00 PM - 8:00 PM",
             20:"8:00 PM - 9:00 PM",
             21:"9:00 PM - 10:00 PM",
             22:"10:00 PM - 11:00 PM",
             23:"11:00 PM - 12:00 PM",
             }

def get_all_tweets(screen_name):
    new_tweets = []
    try:
        localtime = time.localtime(time.time())
        print "Local current time :", localtime
        print "-------Fetching tweets fo User-------", screen_name
        # count = 1
        new_tweets = api.user_timeline(screen_name=screen_name, count=200)
        # import ipdb;ipdb.set_trace()
        [tweets_time.append(tweet.created_at) for tweet in new_tweets]
        # tweets_time.append(new_tweets.created_at)

    except:
        pass
    return new_tweets


class DownloadWorker(Thread):

    def __init__(self, queue):
       Thread.__init__(self)
       self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            screen_name = self.queue.get()
            # import ipdb;ipdb.set_trace()
            get_all_tweets(screen_name)
            self.queue.task_done()


def get_followers(user_name):
    queue = Queue()
    # Create 8 worker threads
    for x in range(8):
        worker = DownloadWorker(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    # screen_names = []
    for page in tweepy.Cursor(api.followers, screen_name=user_name, count=100).pages():
        start_time = time.time()
        print "-------------------------"
        screen_names = [x.screen_name for x in page]
        for screen_name in screen_names:
            queue.put((screen_name))
        end_time = time.time()
        time_take_in_seconds = end_time - start_time
        if int(time_take_in_seconds) < 60:
            time.sleep(60 - int(time_take_in_seconds) + 1)
    queue.join()
    return tweets_time


def update_weekly_and_hourly_stats(tweets_time):
    weekly_status = {}

    for tweet_time in tweets_time:
        day = tweet_time.strftime("%A")
        count = 0
        hour = tweet_time.hour
        hour = hour_dict.get(hour)
        if weekly_status.get((day, hour)):
            count = weekly_status.get((day, hour))

        weekly_status.update({(day, hour): count+1})

    weekly_status = sorted(weekly_status.items(), key=lambda value : value[1], reverse=True)
    # import ipdb;ipdb.set_trace()
    # hourly_status = sorted(hourly_status.items(), key=lambda value : value[1], reverse=True)
    return weekly_status

if __name__ == '__main__':
    user_name = "sudipto_sani"
    get_followers(user_name)
    weekly_status, hourly_status = update_weekly_and_hourly_stats()
    print weekly_status, hourly_status
    import ipdb;ipdb.set_trace()
