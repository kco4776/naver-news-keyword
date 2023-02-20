import asyncio
import argparse
from datetime import datetime, timedelta
from utils import crawling, cleansing
from model import extraction

PRESS_LIST = ['이데일리', '뉴스1', '서울경제']


def main(args):
    now = args.trg

    trg_docs = []
    ref_docs = []
    for d in range(args.gap):
        date = now - timedelta(days=d)
        date = date.strftime('%Y%m%d')

        for press in PRESS_LIST:
            df = asyncio.run(crawling(date, press))
            if d == 0:
                trg_docs += cleansing(df)
            else:
                ref_docs += cleansing(df)

    keywords = extraction(trg_docs, ref_docs)
    print('-'*5+f'{now.strftime("%Y-%m-%d")} KEYWORDS'+'-'*5)
    for i, keyword in enumerate(keywords):
        print(f'{i+1}: {keyword.word.strip()}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--trg',
                        type=lambda s: datetime.strptime(s, '%Y%m%d'),
                        default=datetime.now())
    parser.add_argument('-g', '--gap', default=5)
    args = parser.parse_args()
    main(args)
