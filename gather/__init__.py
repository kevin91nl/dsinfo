import datetime
import logging
import os
import time

from utilities.state import MetaFile


class Scraper:

    @staticmethod
    def is_streaming():
        return False

    def __init__(self, path, sleep_time=1):
        self.datetime_format = '%Y-%m-%d %H:%M:%S'

        # Setup the path
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        # Load the state
        self.metafile = MetaFile(os.path.join(self.path, 'meta.json'))
        self.metadata = {}
        self.load_state()

        # Determine the minimum scraping day
        self.min_date = self.get_state('min_date', None)
        if self.min_date is None:
            self.min_date = datetime.datetime.utcnow()
            self.set_state('min_date', self.min_date.strftime(self.datetime_format))
        else:
            self.min_date = datetime.datetime.strptime(self.min_date, self.datetime_format)

        self.max_date = self.get_state('max_date', None)
        if self.max_date is None:
            self.max_date = datetime.datetime.utcnow()
            self.set_state('max_date', self.max_date.strftime(self.datetime_format))
        else:
            self.max_date = datetime.datetime.strptime(self.max_date, self.datetime_format)

        self.sleep_time = sleep_time

    def get_state(self, key, default=None):
        return self.metadata.get(key, default)

    def set_state(self, key, value):
        logging.debug('Updating state value for "{}" to "{}"'.format(key, value))
        self.metadata[key] = value
        self.save_state()

    def load_state(self):
        logging.debug('Restoring state...')
        self.metadata = self.metafile.read()

    def save_state(self):
        logging.debug('Storing state...')
        self.metafile.write(self.metadata)

    def scrape(self):
        raise NotImplementedError()

    def __call__(self):
        self.scrape()
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)
