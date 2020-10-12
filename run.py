import requests
import os
from multiprocessing import Pool
from bs4 import BeautifulSoup as bs


OUTPUT_FOLDER = 'out'
ANIVERSE_OUTPUT = OUTPUT_FOLDER + '/aniverse.txt'
MOCA_NEWS_OUTPUT = OUTPUT_FOLDER + '/mocanews.txt'
WEBNEWTYPE_OUTPUT = OUTPUT_FOLDER + '/webnewtype.txt'

CACHE_FOLDER = 'cache'
ANIVERSE_CACHE_OUTPUT = CACHE_FOLDER + '/aniverse'
MOCA_NEWS_CACHE_OUTPUT = CACHE_FOLDER + '/mocanews'
WEBNEWTYPE_CACHE_OUTPUT = CACHE_FOLDER + '/webnewtype'

ANIVERSE_MAX_PAGE = 20
WEBNEWTYPE_MAX_PAGE = 10

ANIVERSE_CACHE_ID_LIMIT = 20


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


def scan_aniverse():
    try:
        last_latest_ids = []
        if os.path.exists(ANIVERSE_CACHE_OUTPUT):
            with open(ANIVERSE_CACHE_OUTPUT, 'r') as f:
                last_latest_ids = f.read().split(';')

        latest_ids = last_latest_ids.copy()
        new_ids = []
        stop = False
        obj_list = []
        for page in range(1, ANIVERSE_MAX_PAGE + 1, 1):
            soup = get_soup('https://aniverse-mag.com/archives/category/aniverse/page/%s' % str(page))
            cb_main = soup.find('div', class_='cb-main')
            if cb_main:
                articles = cb_main.find_all('article')
                for article in articles:
                    if article.has_attr('id'):
                        article_id = article['id'].replace('post-', '').strip()
                        try:
                            if article_id not in last_latest_ids:
                                if article_id not in latest_ids:
                                    new_ids += [article_id]
                                h2_tag = article.find('h2')
                                if h2_tag is None:
                                    continue
                                a_tag = h2_tag.find('a')
                                if a_tag:
                                    obj_list.append({'id': article_id, 'title': a_tag.text.strip()})
                            else:
                                stop = True
                                break
                        except:
                            stop = True
                            break
            if stop:
                break

        with open(ANIVERSE_OUTPUT, 'a+', encoding='utf-8', errors='ignore') as f:
            for obj in reversed(obj_list):
                f.write(obj['id'] + ' ' + obj['title'] + '\n')

        latest_ids = new_ids + latest_ids
        with open(ANIVERSE_CACHE_OUTPUT, 'w+', encoding='utf-8') as f:
            for i in range(min(len(latest_ids), ANIVERSE_CACHE_ID_LIMIT)):
                if i > 0:
                    f.write(';' + latest_ids[i])
                else:
                    f.write(latest_ids[i])
        print('Aniverse - Item(s) scanned: ' + str(len(obj_list)))
    except Exception as e:
        print('Error in Aniverse')
        print(e)


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


def scan_webnewtype():
    try:
        last_latest_date = '1900年01月01日 00:00配信'
        if os.path.exists(WEBNEWTYPE_CACHE_OUTPUT):
            with open(WEBNEWTYPE_CACHE_OUTPUT, 'r', encoding='utf-8') as f:
                last_latest_date = f.read()

        latest_date = last_latest_date
        stop = False
        obj_list = []
        for page in range(1, WEBNEWTYPE_MAX_PAGE + 1, 1):
            soup = get_soup('https://webnewtype.com/news/all/%s/' % str(page))
            section = soup.find('section', id='newsList')
            if section:
                lis = section.find_all('li')
                for li in lis:
                    a_tag = li.find('a')
                    news_date = li.find('span', class_='newsDate')
                    if a_tag and a_tag['href'] and news_date and news_date.text.strip() > last_latest_date:
                        if news_date.text.strip() > latest_date:
                            latest_date = news_date.text.strip()
                        article_id = a_tag['href'].split('/')[-2]
                        news_title = li.find('p', class_='newsTitle')
                        obj_list.append({'id': article_id, 'date': news_date.text.strip(),
                                         'title': news_title.text.strip()})
                    else:
                        stop = True
                        break
            if stop:
                break

        with open(WEBNEWTYPE_OUTPUT, 'a+', encoding='utf-8', errors='ignore') as f:
            for obj in reversed(obj_list):
                f.write(obj['id'] + ' ' + obj['date'] + ' ' + obj['title'] + '\n')

        with open(WEBNEWTYPE_CACHE_OUTPUT, 'w+', encoding='utf-8') as f:
            f.write(latest_date)
        print('WebNewType - Item(s) scanned: ' + str(len(obj_list)))
    except Exception as e:
        print('Error in WebNewType')
        print(e)


def run_process(fn):
    fn()


def run():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)

    fns = [scan_aniverse, scan_mocanews, scan_webnewtype]
    with Pool(3) as p:
        results = []
        for fn in fns:
            result = p.apply_async(run_process, (fn,))
            results.append(result)
        for result in results:
            result.wait()


if __name__ == '__main__':
    run()
