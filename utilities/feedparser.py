import datetime
import json
import html2text
import logging
from time import mktime


def convert_html_to_text(text):
    """
    Converts HTML to Markdown.

    Parameters
    ----------
    text : str
        HTML code or plain text.

    Returns
    -------
    str
        Markdown equivalent of the text.
    """
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_links = True
    h.ignore_emphasis = True

    if type(text) != str:
        text = ''
    if '<' in text and '>' in text and '/' in text:
        text = h.handle(text)

    return text


def normalize_feedparser_data(entry, source, author):
    # Set global metadata
    metadata = {
        'source': source,
        'author': author
    }

    # Create a parsed variant of all the entries
    entry_data = entry
    entry_data.update({
        'summary': entry['summary'] if 'summary' in entry else '',
        'summary_detail': entry['summary_detail'] if 'summary_detail' in entry else '',
        'published': entry['published'] if 'published' in entry else '',
        'published_parsed': entry['published_parsed'] if 'published_parsed' in entry else '',
        'updated': entry['updated'] if 'updated' in entry else '',
        'updated_parsed': entry['updated_parsed'] if 'updated_parsed' in entry else '',
        'title': entry['title'] if 'title' in entry else '',
        'id': entry['id'] if 'id' in entry else '',
        'link': entry['link'] if 'link' in entry else entry['pdf_url'] if 'pdf_url' in entry else ''
    })
    entry_data.update(metadata)
    entry_data['summary'] = convert_html_to_text(entry_data['summary'])
    entry_data['summary_detail'] = convert_html_to_text(entry_data['summary_detail'])
    entry_data['text'] = entry_data['summary'] if len(entry_data['summary']) > len(
        entry_data['summary_detail']) else entry_data['summary_detail']

    # Try to process the datetime
    dt = None
    try:
        dt = datetime.datetime.fromtimestamp(mktime(entry_data['updated_parsed']))
    except Exception as exception:
        logging.debug(exception)
    try:
        dt = datetime.datetime.fromtimestamp(mktime(entry_data['published_parsed']))
    except Exception as exception:
        logging.debug(exception)

    if dt is None:
        logging.warning('Error while parsing the date! Continuing...')
    entry_data['created'] = dt.strftime('%Y-%m-%dT%H:%M:%S')

    return entry_data
