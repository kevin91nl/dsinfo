import logging

import arxiv
import datetime
import json
import os

from multiprocessing.pool import ThreadPool
from gather import Scraper
from utilities.feedparser import normalize_feedparser_data


class ArXivScraper(Scraper):

    def __init__(self, *args, category=None, min_date=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category
        self.min_allowed_date = min_date if min_date is not None else datetime.datetime(1970, 1, 1)
        self.min_allowed_date = datetime.datetime(self.min_allowed_date.year, self.min_allowed_date.month,
                                                  self.min_allowed_date.day, 0, 0, 0)

    def scrape(self):
        calls = [
            (self.fetch_results, {'category': self.category, 'forward': True}),
        ]
        if self.min_date > self.min_allowed_date:
            calls.append(
                (self.fetch_results, {'category': self.category, 'forward': False})
            )
        pool = ThreadPool(len(calls))
        results = pool.map_async(lambda x: x[0](**x[1]), calls)
        pool.close()
        pool.join()
        for (found_min_date, found_max_date) in results.get():
            self.min_date = min(self.min_date, found_min_date)
            self.min_date = max(self.min_date, self.min_allowed_date)
            self.max_date = max(self.max_date, found_max_date)
        self.set_state('min_date', self.min_date.strftime(self.datetime_format))
        self.set_state('max_date', self.max_date.strftime(self.datetime_format))

    def fetch_results(self, category=None, forward=False):
        query = [
            'cat:{}'.format(category)
        ]
        sort_by = 'submittedDate'

        if forward:
            min_date = self.max_date.strftime('%Y%m%d%H%M')
            query.append('submittedDate:[{} TO 999999999999]'.format(min_date))
            sort_order = 'ascending'
        else:
            max_date = self.min_date.strftime('%Y%m%d%H%M')
            query.append('submittedDate:[0 TO {}]'.format(max_date))
            sort_order = 'descending'

        if self.min_date < self.min_allowed_date:
            return self.min_allowed_date, self.max_date

        query = ' AND '.join(query)
        results = arxiv.query(
            search_query=query,
            sort_by=sort_by,
            sort_order=sort_order,
            max_results=100
        )
        min_date = self.min_date
        max_date = self.max_date

        for result in results:
            published_date = datetime.datetime(*result['published_parsed'][:6])
            min_date = min(min_date, published_date)
            max_date = max(max_date, published_date)

        # Write the results to disk
        results = list(map(lambda entry: normalize_feedparser_data(entry, 'rss', 'ArXiv'), results))
        for result in results:
            result['category'] = category
            self.write_to_disk(result)

        return min_date, max_date

    def write_to_disk(self, result):
        published_date = datetime.datetime(*result['published_parsed'][:6])
        if published_date < self.min_allowed_date:
            return
        del result['published_parsed']
        del result['updated_parsed']
        folder = os.path.join(self.path, published_date.strftime('%Y-%m-%d'))
        if not os.path.exists(folder):
            os.makedirs(folder)
        path = os.path.join(folder, result['id'].split('/')[-1] + '.json')
        with open(path, 'w') as out_file:
            json.dump(result, out_file)


if __name__ == '__main__':
    ArXivScraper(path=os.path.join('..', 'data', 'demo'), category='cs.CL',
                 min_date=datetime.datetime(2019, 1, 1)).scrape()
