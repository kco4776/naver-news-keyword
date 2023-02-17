import re
import logging
import asyncio
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

URL_PATTERN = re.compile(
    r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\."
    r"([a-zA-Z]){2," r"6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
)
PATTERN = re.compile(r"[^%s]" % "가-힣a-zA-Z")
SPACE_PATTERN = re.compile(r"\s+")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


async def fetch_url(session, url):
    async with session.get(url) as response:
        assert response.status == 200
        return await response.text()


# press: 이데일리, 서울경제, 뉴스1, 연합뉴스, 한국경제TV, 뉴시스
async def get_urls(date, press='이데일리'):
    async with aiohttp.ClientSession() as session:
        trg_urls = []
        url = f'https://finance.naver.com/news/news_list.naver' \
              f'?mode=RANK&date={date}&page=1'
        try:
            html = await fetch_url(session, url)
        except Exception as e:
            logging.error(f"Failed to fetch URL: {url}. Error: {e}")
            return trg_urls

        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logging.error(f"Failed to parse HTML. Error: {e}")
            return trg_urls

        try:
            last = soup.select_one('td.pgRR a')
            last_page = int(last['href'][-1])
        except Exception as e:
            logging.error(f"Failed to get last page. Error: {e}")
            return trg_urls

        try:
            news_list = soup.select('.simpleNewsList li')
            for news in news_list:
                tmp = news.select_one('.press').text.strip()
                if tmp == press:
                    trg_urls.append('https://finance.naver.com' + news.a['href'])
        except Exception as e:
            logging.error(f"Failed to get news list. Error: {e}")
            return trg_urls

        tasks = []
        for i in range(2, last_page + 1):
            url = f'https://finance.naver.com/news/news_list.naver' \
                  f'?mode=RANK&date={date}&page={i}'
            tasks.append(asyncio.ensure_future(fetch_url(session, url)))
        try:
            htmls = await asyncio.gather(*tasks)
        except Exception as e:
            logging.error(f"Failed to gather HTMLs. Error: {e}")
            return trg_urls

        for html in htmls:
            try:
                soup = BeautifulSoup(html, 'html.parser')
            except Exception as e:
                logging.error(f"Failed to parse HTML. Error: {e}")
                continue
            try:
                news_list = soup.select('.simpleNewsList li')
                for news in news_list:
                    tmp = soup.select_one('.press').text.strip()
                    if tmp == press:
                        trg_urls.append('https://finance.naver.com' + news.a['href'])
            except Exception as e:
                logging.error(f"Failed to get news list. Error: {e}")
                continue
        return trg_urls


# 이데일리, 서울경제, 뉴스1
async def crawling(date, press='이데일리'):
    try:
        async with aiohttp.ClientSession() as session:
            total_title = []
            total_contents = []
            urls = await get_urls(date, press=press)

            tasks = [asyncio.ensure_future(fetch_url(session, url)) for url in urls]
            htmls = await asyncio.gather(*tasks)

            for i, html in enumerate(htmls):
                if i > 0 and i % 10 == 0:
                    logging.info(f"{i} html crawling...")
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.select_one('.article_info h3').text.strip()
                photos = soup.select('.articleCont .end_photo_org')
                if len(photos) != 0:
                    for p in photos:
                        p.extract()
                soup.select_one('.articleCont .link_news').extract()
                contents = soup.select_one('.articleCont').text.strip()

                total_title.append(title)
                total_contents.append(contents)

        df = pd.DataFrame({
            'title': total_title,
            'contents': total_contents,
            'url': urls
        })

        logging.info(f'{date} {press} crawl complete!')
        return df

    except Exception as e:
        logging.exception(f"An error occurred during crawling: {e}")


# 이데일리, 서울경제, 뉴스1
def cleansing(df):
    docs = []
    press_pattern = re.compile('\[.+\]')

    for i, d in df.iterrows():
        if i > 0 and i % 10 == 0:
            logging.info(f"{i} docs cleansing...")
        title, contents, url = d
        tmp = ''
        if not pd.isna(title):
            tmp += title
        if not pd.isna(contents):
            tmp += ' ' + contents
        tmp = press_pattern.sub('', tmp)
        tmp = URL_PATTERN.sub(' ', tmp)
        tmp = PATTERN.sub(' ', tmp)
        tmp = SPACE_PATTERN.sub(' ', tmp)
        if len(''.join(tmp.split())) > 25:
            docs.append(tmp)
    return docs
