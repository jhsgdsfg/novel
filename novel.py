import requests
from pyquery import PyQuery as pq
from urllib.parse import urljoin
import re
from loguru import logger
import time
import sys

SESSION = requests.Session()
BASE_URL = 'https://www.biquge.co/'
BOOK_ID = '21_21675/'
BOOK = open('txt/我在末世有套房_晨星LL_UTF8.txt', 'w', encoding='utf8')
COUNT = 0
logger.remove()
logger.add(sys.stderr, level='INFO')

def scrape_page(url):
    global SESSION
    res = SESSION.get(url)
    res.raise_for_status()
    res.encoding = 'gbk'
    return res

def scrape_index(url):
    url = urljoin(BASE_URL, url)
    return scrape_page(url).text

def scrape_chapter(url):
    url = urljoin(BASE_URL, url)
    return scrape_page(url).text

def parse_index(html):
    doc = pq(html)
    dts = doc('#list dl dt').items()
    for dt in dts:
        if '正文' in dt.text():
            dds = dt.next_until('#dahengfu').items()
    chapters = []
    for dd in dds:
        url = dd('a').attr('href')
        chapters.append(url)
    return chapters

def parse_chapter(html):
    doc = pq(html)
    title = doc('.bookname h1').text()
    text = doc('#content').text()
    text = re.sub('\n\n', '\n', text)
    return {'title': title, 'text': text}

def save_data(data):
    global COUNT, BOOK
    title = data['title']
    text = data['text']
    BOOK.write(f'{title}\n{text}\n')
    COUNT += 1

def main():
    global BASE_URL, BOOK_ID, COUNT
    index = scrape_index(BOOK_ID)
    logger.info('scraped index: {}', urljoin(BASE_URL, BOOK_ID))
    chapters = parse_index(index)
    logger.info('parsed index: {}', len(chapters))

    for chapter in chapters:
        logger.info('scraping chapter: {}', chapter)
        html = scrape_chapter(chapter)
        data = parse_chapter(html)
        logger.debug(data['title'])
        logger.debug(data['text'][:100])
        save_data(data)
        logger.info(COUNT)
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    finally:
        BOOK.close()
        SESSION.close()