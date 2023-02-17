# Naver Economic News Crawler and Keyword Extractor
This project is a Python-based web crawler that searches for news articles related to the economy and extracts keywords from them.

한글과 영어를 제외한 모든 문자 ```가-힣a-zA-Z``` 를 제거 합니다. [soynlp](https://github.com/lovit/soynlp) 비지도학습을 통해 명사들만을 추출한후 trg_date에 대한 ref_date들의 단어 출현 확률을 기반으로 키워드를 정의합니다. 
자세한 내용은 [이곳](https://github.com/lovit/soykeyword/blob/master/tutorials/keyword_extraction_using_proportion_ratio.ipynb)에 있습니다.

## Requirements
- Python 3.x
- aiohttp
- beautifulsoup4
- pandas

## Installation
Clone the repository:
```console
git clone https://github.com/kco4776/naver-news-keyword.git
```
Install the dependencies:
```console
pip install -r requirements.txt
```

## Usage
```console
python main.py -t <target_date> -g <gap>
```
where <target_date> is the target date in the format YYYYMMDD and <gap> is the number of days to go back from the target date to extract articles from.

The crawler extracts articles from three news sites: ```이데일리, 뉴스1, 서울경제```

## Contributing
If you want to contribute to this project, please fork the repository and create a pull request.

## License
This project is licensed under the MIT License.
