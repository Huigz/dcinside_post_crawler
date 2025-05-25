# DCinside Scrapy 프로젝트

## 프로젝트 구조
```
dcinside_scrapy/
├── dcinside_scrapy/
│   ├── __init__.py
│   ├── items.py          # 데이터 모델 정의
│   ├── middlewares.py    # 미들웨어 （이 프로젝트에서 미사용）
│   ├── pipelines.py      # 데이터 처리 파이프라인 （이 프로젝트에서 미사용）
│   ├── settings.py       # 프로젝트 설정
│   └── spiders/          # 크롤러 디렉토리
│       ├── __init__.py
│       └── dcinside_spider.py  # 메인 크롤러 파일
├── scrapy.cfg            # Scrapy 설정 파일
└── README.md    

example_result.csv # 수집된 데이터 예제        
```

## 데이터 필드
- artist: 아티스트 이름
- month: 게시 시간 (월)
- url: 게시글 URL
- nickname: 작성자 닉네임
- ip: 작성자 IP
- uid: 작성자 ID (고정닉)
- title: 게시글 제목
- like: 추천수
- unlike: 비추천
- view: 조회수
- content: 게시글 내용

## 사용 방법

1. CSV 파일 준비 (다음 열 포함):
   - Url: 수집할 게시글 URL
   - Artist: 아티스트 이름
   - Month: 게시 시간 (월)

2. 크롤러 실행:

```bash
scrapy crawl dcinside -a csv_file=your_file.csv -o file_to_save_data.csv
```

예:

```bash
scrapy crawl dcinside -a csv_file=data/urls.csv -o example_result.csv
```

