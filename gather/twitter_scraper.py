import json
import os
import re
import time

import tweepy

from tweepy import StreamListener, Stream

from gather import Scraper


class TwitterScraper(Scraper, StreamListener):

    @staticmethod
    def is_streaming():
        return True

    def __init__(self, path, consumer_token, consumer_secret, access_token, access_secret, track, languages, **kwargs):
        super().__init__(path, **kwargs)
        self.auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        self.auth.set_access_token(access_token, access_secret)
        self.track = track
        self.languages = languages

    def __call__(self):
        stream = Stream(self.auth, self)
        stream.filter(track=self.track.split(','), languages=self.languages.split(','))

    def on_data(self, data):
        # Normalize fields
        data_dict = json.loads(data)

        data_dict['source'] = 'twitter'
        data_dict['author'] = data_dict.get('user', {}).get('name', None)
        data_dict['text'] = data_dict.get('text', None)
        if 'full_text' in data_dict:
            data_dict['text'] = data_dict['full_text']
        if 'extended_tweet' in data_dict and 'full_text' in data_dict['extended_tweet']:
            data_dict['text'] = data_dict['extended_tweet']['full_text']

        if 'retweeted_status' in data_dict:
            # Weird behaviour; sometimes the full text is only available in the retweeted_status field
            # This code makes sure that the full text will not be abbreviated by Twitter
            retweeted_status = data_dict['retweeted_status']
            retweeted_text = retweeted_status.get('text', None)
            if 'full_text' in retweeted_status:
                retweeted_text = retweeted_status['full_text']
            if 'extended_tweet' in retweeted_status and 'full_text' in retweeted_status['extended_tweet']:
                retweeted_text = retweeted_status['extended_tweet']['full_text']
            rt_text = re.search('(^RT @[^:]+: )', data_dict.get('text', ''))
            if rt_text:
                retweeted_text = rt_text.group(0) + retweeted_text
            data_dict['text'] = retweeted_text

        data_dict['id'] = data_dict.get('id', None)
        data_dict['created'] = data_dict.get('created_at', None)
        data_dict['link'] = 'https://twitter.com/statuses/' + str(data_dict['id']) + '/'
        if data_dict.get('created') is not None:
            data_dict['created'] = time.strftime('%Y-%m-%dT%H:%M:%S%z', time.strptime(data_dict.get('created'),
                                                                                      '%a %b %d %H:%M:%S +0000 %Y'))

        # Write to disk
        folder = os.path.join(self.path,
                              time.strftime('%Y-%m-%d', time.strptime(data_dict.get('created'), '%Y-%m-%dT%H:%M:%S%z')))
        if not os.path.exists(folder):
            os.makedirs(folder)
        path = os.path.join(folder, str(data_dict['id']) + '.json')
        with open(path, 'w') as out_file:
            json.dump(data_dict, out_file)

        return True

    def on_error(self, status):
        print(status)
