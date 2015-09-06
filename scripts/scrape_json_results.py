#!env/bin/python

import logging
import time
from datetime import datetime, timedelta
import json
import urllib.request, urllib.error

logging.basicConfig(level=logging.DEBUG)

DATE_FORMAT = '%Y-%m-%d  '
RETRY_DELAY = 1 # in seconds
WEBSITES = {
    # 'name': ('url', get_max_articles(json), get_article_list(json), page_start, calculate_count(count))
    # 'akamaihd': ('https://md1-a.akamaihd.net/sitesearch-api/search.jsonp?query=e&sort=displaydatetime+desc&startat={}', 0),
    'usatoday': {
        'url':          'http://www.usatoday.com/search/e/{}/?ajax=true',
        'get_max':      lambda json: json['results']['total'],
        'get_urls':     lambda json: [doc['contenturl'] for doc in json['results']['documents']],
        'calc_count':   lambda article_count: article_count,
        'page_start':   1,
        'date_loop':    False
    },
    'nytimes': {
        # 'url':          'http://query.nytimes.com/svc/add/v1/sitesearch.json?end_date=20150813&begin_date=20140813&sort=desc&page={}&facet=true',
        'url':          'http://query.nytimes.com/svc/add/v1/sitesearch.json?end_date={date}&begin_date={date}&sort=desc&page={}&facet=true',
        'get_max':      lambda json: json['response']['meta']['hits'],
        'get_urls':     lambda json: [doc['web_url'] for doc in json['response']['docs']],
        'calc_count':   lambda article_count: int(article_count / 10), # 10 articles/page
        'page_start':   0,
        'date_loop':    True,
        'date_format':  '%Y%m%d',
        'start_date':   datetime(year=2015, month=8, day=13),
        'end_date':     datetime(year=2014, month=8, day=13),
        'timedelta':    timedelta(days=-1),
    }
}
OUTPUT_FILENAME = 'output.csv'

def open_json_url(url, count):
    logging.debug("url: {}".format(url.format(count)))
    success = False
    while not success:
        try:
            url_fd = urllib.request.urlopen(url.format(count))
            success = True
        except urllib.error.URLError as e:
            logging.warn('Trying again: {}'.format(e))
            time.sleep(RETRY_DELAY)
    return json.loads(url_fd.read().decode())

def scrape(website_info, fd, initial_count=0):
    if website_info.pop('date_loop', False):
        url = website_info.pop('url')
        date_format = website_info.pop('date_format')
        start_date = date = website_info.pop('start_date')
        end_date = website_info.pop('end_date')
        date_delta = website_info.pop('timedelta')

        count = initial_count
        lost_articles = 0
        while start_date <= date <= end_date or end_date <= date <= start_date:
            info = website_info.copy()
            info['url'] = url.format('{}', date=date.strftime(date_format))
            page_count, page_lost = scrape_page(info, fd, initial_count, date)
            count += page_count
            lost_articles += page_lost
            logging.debug("count: {}".format(count))
            # Just to make sure we don't lose anything
            fd.flush()
            date += date_delta
        return count, lost_articles

    else:
        return scrape_page(website_info, fd, count)

def scrape_page(website_info, fd, count=0, date=None):
    url = website_info.pop('url')
    get_max = website_info.pop('get_max')
    get_urls = website_info.pop('get_urls')
    calc_count = website_info.pop('calc_count')
    page_start = website_info.pop('page_start')
    get_date = website_info.pop('get_date') if date is None else lambda _, date=date: date

    lost_articles = 0
    # Very ugly coding. This variable is used in the loop to to access the
    # number of urls on the previous page.
    one_page_count = 0
    max_articles = None
    while max_articles is None or count < max_articles:
        logging.debug(datetime.now().strftime("time: %H:%M:%S"))
        logging.debug("count: {}".format(count))

        try:
            json = open_json_url(url, calc_count(count))
        except urllib.error.HTTPError as e:
            # nytimes gives 400 at too high a page count
            if e.code == 400:
                action = 'Skipping to next date (discarding the remaining urls)'
                e.msg = 'Max page count exceeded'
                lost = max_articles - count
            elif e.code == 500:
                action = 'Skipping to next page (discarding 10 urls)'
                e.msg = 'Internal server error'
                lost = one_page_count
            else:
                raise e

            message = '{action} ({count} of {max} urls successful, lost {lost}): {error}'.format(
                action=action,
                count=count,
                max=max_articles,
                lost=lost,
                error=e
            )
            logging.warn(message)
            fd.write(message + '\n')

            if e.code == 400:
                break
            elif e.code == 500:
                lost_articles += lost
                count += lost
                continue

        if max_articles is None:
            max_articles = int(get_max(json))
            logging.debug("Max articles: {}".format(max_articles))
        urls = get_urls(json)
        one_page_count = len(urls)
        count += one_page_count
        # Add a newline after each url
        urls = map(
            lambda url: get_date(url).strftime(DATE_FORMAT) + url + '\n',
            urls
        )
        fd.write(''.join(urls))
    return count - lost_articles, lost_articles

if __name__ == '__main__':
    # Input
    import argparse
    parser = argparse.ArgumentParser(description='Scrape urls from a webpage')
    parser.add_argument('website_id', metavar='id of website to be scraped', nargs=1)
    parser.add_argument('output_filename', metavar='output file', nargs='?',
                        help='File to output urls to')
    args = parser.parse_args()
    output_filename = args.output_filename or OUTPUT_FILENAME

    if args.website_id[0] in WEBSITES:
        website_info = WEBSITES[args.website_id[0]]
        logging.debug('website_info: {}'.format(website_info))
    else:
        print("Unknown website id, choose one of: {}".format(WEBSITES.keys()))
        exit(1)

    with open(output_filename, 'w') as fd:
        logging.info("Started scraping")
        count, lost_articles = scrape(website_info, fd)
    logging.info("Found {} urls, missed {}".format(count, lost_articles))
