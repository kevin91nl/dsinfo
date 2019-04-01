import datetime
import json
import glob
import math
import operator
import os
import time
from argparse import ArgumentParser

from nltk import ngrams
from nltk.corpus import stopwords
import re
import string
from collections import defaultdict

# count_freq = defaultdict(int)
# count_docs = defaultdict(int)
# files = 'data/arxiv/cs.AI/2019-03/*.json'
# files = glob.glob(files)
# num_docs = len(files)
# for file in files:
#     with open(file, 'r') as in_file:
#         data = json.load(in_file)
#     doc_terms = defaultdict(int)
#     for word in data['summary'].split(' '):
#         count_freq[word.lower()] += 1
#         doc_terms[word.lower()] = 1
#     for word in doc_terms:
#         count_docs[word.lower()] += doc_terms[word.lower()]
#
# for item in sorted(count_docs.items(), key=lambda item: item[1], reverse=False):
#     print(item)

import logging
from collections import Counter


class ComputeTfIdf:

    def __init__(self, to_lower=True, remove_punctuation=True):
        self.to_lower = to_lower
        self.remove_punctuation = remove_punctuation

    def __call__(self, texts):
        tf = Counter()
        df = Counter()
        N = len(texts)
        for text in texts:
            if self.remove_punctuation:
                text = re.sub("[']{1}[a-z]{1, 4}", '', text)
                text = re.sub('[' + re.escape(string.punctuation) + ']{1}', ' ', text)
            words = text.split()
            words = list(ngrams(words, 1)) + list(ngrams(words, 2))
            words = [' '.join(word) for word in words]
            if self.to_lower:
                words = list(map(lambda word: word.lower(), words))
            for word in words:
                tf[word] += 1
            for word in set(words):
                df[word] += 1
        tfidfs = {}
        for word in df:
            occurrence_ratio = df[word] / N
            idf = math.log(N / df[word])
            tfidf = tf[word] * idf
            tfidfs[word] = {
                'tfidf': tfidf,
                'df': df[word],
                'idf': idf,
                'occurrence_ratio': occurrence_ratio
            }
        return tfidfs


class Analyzer:

    def __init__(self, path, window):
        self.path = path
        self.window = window

    def get_entries(self, pattern='.*'):
        min_date = datetime.datetime.now() - datetime.timedelta(days=self.window)
        folders = os.listdir(self.path)
        files = []
        for folder in folders:
            if not re.match(pattern, folder):
                continue
            path = os.path.join(self.path, folder)
            if os.path.isdir(path):
                date_folders = os.listdir(path)
                for date_folder in date_folders:
                    if date_folder >= min_date.strftime('%Y-%m-%d'):
                        data_path = os.path.join(path, date_folder)
                        subfiles = glob.glob(os.path.join(data_path, '*.json'))
                        files.extend(subfiles)

        entries = []
        texts = []
        for file in files:
            with open(file, 'r') as in_file:
                try:
                    entry = json.load(in_file)
                except:
                    continue
                entries.append(entry)
                texts.append(entry)

        return texts


class TfIdfAnalyzer(Analyzer):

    def __call__(self):
        stopwords_dict = {word: True for word in stopwords.words('english')}
        stopwords_dict.update({
            word: True for word in [
            'rt', 'one', 'two', 'set', 'amp', 'real', 'e', 'rt', 'used', 'new', 'many', 'also', 'show', 'using', 'low',
            'use', 'non', '1', 'provide', 'first', 'second', 'like', 'well', 'better', 'via', 'good', 'end', 'three',
            '3', 'however', 'large', 'find', 'novel', 'high', 'multi'
        ]
        })
        texts = [entry['text'] for entry in self.get_entries('arxiv*') if entry is not None and 'text' in entry]
        compute_tfidf = ComputeTfIdf(to_lower=True, remove_punctuation=True)
        stats = compute_tfidf(texts)
        stats = stats.items()
        stats = list(filter(lambda x: x[1]['df'] >= 3, stats))
        stats = list(filter(lambda x: x[1]['occurrence_ratio'] <= 0.5, stats))
        stats = [stat for stat in stats if sum(word in stopwords_dict for word in stat[0].split()) == 0]
        stats = sorted(stats, key=lambda x: x[1]['tfidf'])
        results = []
        for stat in stats:
            result = {}
            result.update(stat[1])
            result.update({'word': stat[0]})
            results.append(result)
        results = results[-100:]

        if not os.path.exists('webapp/static/data'):
            os.makedirs('webapp/static/data')

        with open(os.path.join('webapp/static/data', 'words.json'), 'w') as out_file:
            json.dump({
                'stats': results
            }, out_file)


class Summarizer(Analyzer):

    def __call__(self):
        entries = self.get_entries('arxiv*')

        papers = defaultdict(list)
        for entry in entries:
            if 'arxiv_comment' in entry:
                comment = entry['arxiv_comment']
                if comment:
                    if 'accepted as' in comment.lower() or 'accepted on' in comment.lower() or 'accepted in' in comment.lower() or 'accepted for' in comment.lower() or 'accepted at' in comment.lower() or 'accepted to' in comment.lower() or 'accepted by' in comment.lower():
                        papers[entry['title']].append({
                            'category': entry['category'],
                            'title': entry['title'],
                            'date': entry['published'].split('T')[0],
                            'link': entry['link'],
                            'comment': entry['arxiv_comment'] if 'arxiv_comment' in entry else ''
                        })

        # Unduplicate titles
        all_papers = []
        for title in papers:
            paper = papers[title][0]
            categories = []
            for subpaper in papers[title]:
                categories.append(subpaper['category'])
            paper['category'] = ', '.join(sorted(categories))
            all_papers.append(paper)

        all_papers = sorted(all_papers, key=operator.itemgetter('date'), reverse=True)

        if not os.path.exists('webapp/static/data'):
            os.makedirs('webapp/static/data')

        with open(os.path.join('webapp/static/data', 'papers.json'), 'w') as out_file:
            json.dump({
                'papers': all_papers
            }, out_file)


if __name__ == '__main__':
    parser = ArgumentParser('Analyzer for creating insights out of the data.')
    parser.add_argument('--path', help='The path to use.')
    parser.add_argument('--window', help='The number of days to read data from.', type=int, default=7)
    args = parser.parse_args()

    while True:
        Summarizer(args.path, args.window)()
        TfIdfAnalyzer(args.path, args.window)()
        time.sleep(10)
