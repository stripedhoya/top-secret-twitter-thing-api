#!/usr/bin/env python
import ConfigParser
import os

import redis
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.api import API
from tweepy.streaming import StreamListener


class MyStreamListener(StreamListener):
    def __init__(self):
        self.api = API()
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.abspath('config.ini'))
        self.r = redis.StrictRedis(host=self.config.get('DB', 'host'), port=self.config.get('DB', 'port'))

    def on_status(self, status):
        """

        :param status:
        :return:
        """
        tweet = status._json
        if tweet['entities']['hashtags'][0]['text'] == 'wifihasfallen':
            location = tweet['text'][15:]
            self.r.set(location, 'Wifi is Down')
        else:
            location = tweet['text'][17:]
            self.r.set(location, 'Wifi is UP')


def auth():
    """
    Sets up OAuth token for use with Twitter's API
    :return:
    """
    config = ConfigParser.ConfigParser()
    config.read(os.path.abspath('config.ini'))

    token = OAuthHandler(config.get('Twitter_Keys', 'consumer_key'),
                         config.get('Twitter_Keys', 'consumer_secret'))
    token.set_access_token(config.get('Twitter_Keys', 'access_token'),
                           config.get('Twitter_Keys', 'access_secret'))
    return token

if __name__ == '__main__':
    myStreamListener = MyStreamListener()
    token = auth()

    myStream = Stream(auth=token, listener=myStreamListener)
    try:
        myStream.filter(track=['#wifihasfallen', '#returnthewifihas'])
    except Exception as e:
        pass
