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
```

## 기능 설명
- DCinside 웹사이트에서 게시글 데이터 수집
- CSV 파일에서 URL 목록 읽기 지원
- 한글과 영어 텍스트 자동 처리
- 게시글 제목, 작성자, 내용 등 정보 추출

## 데이터 필드
- artist: 아티스트 이름
- month: 월
- url: 게시글 URL
- nickname: 작성자 닉네임
- ip: 작성자 IP
- post_id: 게시글 ID
- title: 게시글 제목
- like: 좋아요 수
- unlike: 싫어요 수
- view: 조회수
- content: 게시글 내용

## 사용 방법
1. CSV 파일 준비 (다음 열 포함):
   - Url: 게시글 URL
   - Artist: 아티스트 이름
   - Month: 월

2. 크롤러 실행:
```bash
scrapy crawl dcinside -a csv_file=your_file.csv -o file_to_save_data.csv
```

## 데이터 정제
- 한글과 영어가 아닌 문자 자동 제거
- 일반 공백 유지
- 숫자 자동 추출
- 빈 값 자동 처리


