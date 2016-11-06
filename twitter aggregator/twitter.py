#!/usr/bin/env python 
"""
    Author: Rowland DePree
    Created Date: 11/05/2016

    A script to query Twitter to see if there are any Wifi routers down in certain areas

"""
import ConfigParser
import os
import time
from datetime import datetime

import pytz
import redis
import tweepy


class Twitter:
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.abspath('config.ini'))
        self.r = redis.StrictRedis(host=self.config.get('DB', 'host'), port=self.config.get('DB', 'port'))
        self.token = self.auth()

    def auth(self):
        """
        Sets up OAuth token for use with Twitter's API
        :return:
        """
        token = tweepy.OAuthHandler(self.config.get('Twitter_Keys', 'consumer_key'),
                                    self.config.get('Twitter_Keys', 'consumer_secret'))
        token.set_access_token(self.config.get('Twitter_Keys', 'access_token'),
                               self.config.get('Twitter_Keys', 'access_secret'))

        token.wait_on_rate_limit = True
        token.wait_on_rate_limit_notify = True
        token.retry_count = 5

        return token

    def down_search(self, q, geocode, epoch_time, dict):
        """
        A search function that will search twitter and insert into redis the result
        :param q: string, search criteria
        :param geocode: tuple, latitude, longitude, radius (either mi or km)
        :param epoch_time: int, the epoch time
        :return: boolean
        """
        token = tweepy.API(self.token)
        count = 0
        results = token.search(q, geocode=geocode, count=100, result_type='recent')
        if results:
            for status in results:
                utc_time = datetime.strptime(str(status._json['created_at']), '%a %b %d %H:%M:%S +0000 %Y').replace(
                    tzinfo=pytz.UTC)
                tweet_epoch = (utc_time - datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)).total_seconds()
                if tweet_epoch <= epoch_time:
                    count += 1

        if count > 4:
            self.insert_redis(geocode, 'Wifi is DOWN')
            dict[geocode] = True

    def backup_search(self, q, geocode, epoch_time, dict):
        """
        A search function that will search twitter and insert into redis the result
        :param q: string, search criteria
        :param geocode: tuple, latitude, longitude, radius (either mi or km)
        :param epoch_time: int, the epoch time
        :return: boolean
        """
        token = tweepy.API(self.token)
        count = 0
        results = token.search(q, geocode=geocode, count=100, result_type='recent')
        if results:
            for status in results:
                utc_time = datetime.strptime(str(status._json['created_at']), '%a %b %d %H:%M:%S +0000 %Y').replace(
                    tzinfo=pytz.UTC)
                tweet_epoch = (utc_time - datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)).total_seconds()
                if tweet_epoch <= epoch_time:
                    count += 1

        if count > 4:
            self.insert_redis(geocode, 'Wifi is UP')
            dict[geocode] = False

    def insert_redis(self, key, value):
        """
        Inserts into a redis database
        :param key: string
        :param value: string
        :return:
        """
        self.r.set(key, value)


if __name__ == '__main__':
    twt = Twitter()
    loc_dict = {'38.906364,-77.074541,0.5mi': False, '38.908009, -77.075352,0.5mi': False,
                '38.910188, -77.074614,0.5mi': False}
    while True:
        min = time.localtime((time.time()))[4]
        if min == 0 or min % 5 == 0:
            if loc_dict['38.906364,-77.074541,0.5mi']:
                twt.backup_search('wifi down', '38.906364,-77.074541,0.5mi', time.time(), loc_dict)
            else:
                twt.down_search('wifi down', '38.906364,-77.074541,0.5mi', time.time(), loc_dict)
            if loc_dict['38.908009, -77.075352,0.5mi']:
                twt.backup_search('wifi down', '38.908009, -77.075352,0.5mi', time.time(), loc_dict)
            else:
                twt.down_search('wifi down', '38.908009, -77.075352,0.5mi', time.time(), loc_dict)
            if loc_dict['38.910188, -77.074614,0.5mi']:
                twt.backup_search('wifi down', '38.910188, -77.074614,0.5mi', time.time(), loc_dict)
            else:
                twt.down_search('wifi down', '38.910188, -77.074614,0.5mi', time.time(), loc_dict)
