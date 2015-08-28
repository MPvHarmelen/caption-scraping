#!env/bin/python

import logging
import json
import urllib.request

logging.basicConfig(level=logging.INFO)

WEBSITES = {
    # 'name': ('url', get_max_articles(json), get_article_list(json), page_start, calculate_count(count))
    # 'akamaihd': ('https://md1-a.akamaihd.net/sitesearch-api/search.jsonp?query=e&sort=displaydatetime+desc&startat={}', 0),
    'usatoday': (
        'http://www.usatoday.com/search/e/{}/?ajax=true',
        lambda json: json['results']['total'],
        lambda json: [doc['contenturl'] for doc in json['results']['documents']],
        lambda article_count: article_count,
        1
    ),
    'nytimes': (
        'http://query.nytimes.com/svc/add/v1/sitesearch.json?end_date=20150813&begin_date=20140813&sort=desc&page={}&facet=true',
        lambda json: json['response']['meta']['hits'],
        lambda json: [doc['web_url'] for doc in json['response']['docs']],
        lambda article_count: int(article_count / 10), # 10 articles/page
        0
    )
}
OUTPUT_FILENAME = 'output.csv'

def open_json_url(url, count):
    logging.debug("url: {}".format(url.format(count)))
    return json.loads(urllib.request.urlopen(url.format(count)).read().decode())

def scrape(website_info, fd, count=0):
    url, get_max, get_urls, calc_count, page_start = website_info

    max_articles = int(get_max(open_json_url(url, page_start)))
    while count < max_articles:
        logging.debug("Count: {}".format(count))
        urls = get_urls(open_json_url(url, calc_count(count)))
        logging.debug('{}: {}'.format(url[:30], len(urls)))
        count += len(urls)
        # Add a newline after each url
        urls = map(
            lambda url: url + '\n',
            urls
        )
        fd.write(''.join(urls))
    return count

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
    else:
        print("Unknown website id, choose one of: {}".format(WEBSITES.keys()))
        exit(1)

    logging.info("Started scraping")
    with open(output_filename, 'w') as fd:
        logging.debug("Started scraping")
        count = scrape(website_info, fd)
    logging.info("Found {} urls".format(count))
