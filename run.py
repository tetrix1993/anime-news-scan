import requests
import os
from bs4 import BeautifulSoup as bs


OUTPUT_FOLDER = 'out'
ANIVERSE_OUTPUT = OUTPUT_FOLDER + '/aniverse.txt'
MOCA_NEWS_OUTPUT = OUTPUT_FOLDER + '/mocanews.txt'
WEBNEWTYPE_OUTPUT = OUTPUT_FOLDER + '/webnewtype.txt'

CACHE_FOLDER = 'cache'
ANIVERSE_CACHE_OUTPUT = CACHE_FOLDER + '/aniverse'
MOCA_NEWS_CACHE_OUTPUT = CACHE_FOLDER + '/mocanews'
WEBNEWTYPE_CACHE_OUTPUT = CACHE_FOLDER + '/webnewtype'


def get_soup(url, headers=None, encoding=None):
    if headers == None:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    try:
        result = requests.get(url, headers=headers)
        if encoding:
            result.encoding = encoding
            return bs(result.content.decode(encoding, 'ignore'), 'html.parser')
        return bs(result.text, 'html.parser')
    except Exception as e:
        print(e)
    return ""


def scan_mocanews():
    try:
        latest_id = '0000000000000a_'
        if os.path.exists(MOCA_NEWS_CACHE_OUTPUT):
            with open(MOCA_NEWS_CACHE_OUTPUT, 'r') as f:
                latest_id = f.read()

        scan_count = 0
        soup = get_soup('https://moca-news.net/', encoding='shift_jis')
        linkblocks = soup.find('div', id='main-area').find_all('div', class_='linkblock')
        for linkblock in reversed(linkblocks):
            if linkblock.has_attr('name'):
                continue
            if linkblock.has_attr('onclick') and 'article' in linkblock['onclick']:
                split1 = linkblock['onclick'].split('/')
                id = split1[3]
                if id > latest_id:
                    latest_id = id
                    fontbold_div = linkblock.find('div', class_='fontbold')
                    if fontbold_div:
                        with open(MOCA_NEWS_OUTPUT, 'a+', encoding='utf-8', errors='ignore') as f:
                            f.write(id + ' ' + fontbold_div.text[2:] + '\n')
                        scan_count += 1
        with open(MOCA_NEWS_CACHE_OUTPUT, 'w+') as f:
            f.write(latest_id)
        print('Moca News - Item(s) scanned: ' + str(scan_count))
    except Exception as e:
        print('Error in Moca News')
        print(e)


def run():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)
    scan_mocanews()


if __name__ == '__main__':
    run()
