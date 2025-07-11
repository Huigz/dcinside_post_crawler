
**2025.7.12**

- [Update] New progress bar :tada:
- [Update] You can now use `url.csv` column names in any case variant (e.g., Artist, ARTIST, artist, etc.). :tada:
- [Settings] Default delay: 0.7 s :rocket:
- [Settings] Change Url CSV file column format: Month → Date (`yyyy-mm` → `yyyy-mm-dd`) :warning:

2025.6.17
- [update] delay time setting (아래 설정 방법 4.2 참조)
- [fix] contents filter (특수 이모티콘만 제거)

2025.6.14
- [update] process bar 기능
- [update] fake useragent 기능
- [fix] crawler request speed 조절 
- [debug] log내용 "logs/dcinside.log"에서 저장
- [debug] 연결이 성공했지만 데이터 수집 안된 경우 오류 생긴 html file "debug_warning_html/*.html"에서 저장

# DCInside Scrapy Crawler Guide 

> [!CAUTION]
> Python=3.11 환경에서 개발/테스트완료
> 기타 버전에서 실행 시 오류 생길 수 있음


### 1. Download & Clone the project 

- Download directly 

  - https://github.com/Huigz/dcinside_post_crawler/archive/refs/heads/main.zip
    - 다운로드가 완료되면  **dcinside_post_crawler-main.zip** 파일을 로컬에 압축 해제(Unzip)해 주세요.

- Or Use Git and clone the project in bash

  ```bash
  git clone https://github.com/Huigz/dcinside_post_crawler.git
  ```


### 2. Open Terminal & Command Line

**2.1. 프로젝트 경로로 이동**

```bash
cd path_of_your_project
```

> [!NOTE]
>
> 압축을 해제(Unzip)한 파일의 경로가 /Users/jmsu/Downloads/main 이라고 가정하면
>
> ```bash
> cd /Users/jmsu/Downloads/main/
> ```
>

**2.2. 운행에 필요할 python packages 설치**

```bash
pip install -r requirments.txt
```

### 3. Put your url.csv File in data folder

> [!NOTE]
>
> 프로젝트 에는 이미 예제 url.csv 파일이 존재하며, 위치는 다음과 같다
>
> - data/urls.csv



Scrapy는 urls.csv 파일의 url 열 데이터를 순차적으로 추가하고, 각 URL에 대해 자동으로 서버에게 요청을 보냅니다. 이때, urls.csv 파일은 다음과 같은 요구 사항을 반드시 충족해야 한다.

1. **파일 형식**

   - 파일명: `urls.csv`

   - 인코딩: UTF-8

   - 구분자: 콤마(,)

2. **필수 열**

> [!IMPORTANT]
> Update 7.12 
> You can now use `url.csv` column names in any case variant (e.g., Artist, ARTIST, artist, etc.).


​	CSV 파일은 반드시 다음 세 개의 열(3 columns)을 포함해야 한다:

- `Url`: DCinside 게시글 URL
  - URL은 반드시 DCinside 갤러리의 게시글 URL이어야 한다

- `Artist`: 아티스트 이름
- `Date`: 게시글 작성 월

> [!NOTE]
>
> 예.
>
> ```
> Url,Artist,Date
> https://gall.dcinside.com/board/view/?id=artist&no=1234567,아이유,2024-03
> https://gall.dcinside.com/board/view/?id=artist&no=7654321,IU,2024-02
> ```



### 4. Run scrapy
#### 4.1 start crawling
```bash
scrapy crawl dcinside -a csv_file=path_of_url_file
```

> [!IMPORTANT]
>
> Url.csv 파일을 프로젝트 Root 디렉터리의 data 폴더에 저장했기 때문에, 파일명이 **urls.csv** 라고 가정하면 **path_of_url_file** 은 다음과 같다
>
> - data/urls.csv
>
> 수집한 데이터가 자동으로 프로젝트 Root 디렉터리의 **result.csv** 파일에 저장된다
>
> - result.csv
>

따라서 위의 전제를 바탕으로 Scrapy crawler를 실행하는 명령어는 다음과 같다:

```bash
scrapy crawl dcinside -a csv_file=data/urls.csv
```


> [!CAUTION]
>
> Scrapy는 자동으로 result.csv 파일을 생성하며, **처음 크롤러를 실행할 때 동일한 디렉터리에 같은 이름의 result.csv 파일이 존재하지 않도록 주의해 주세요.**


#### 4.2 set crawling delay time

default delay time = 2

**You can set it to 1 second ⬇️ or any value you want.**

```bash
scrapy crawl dcinside -a csv_file=data/urls.csv -a delay=1
```

### 5. Resume the crawling process

#### 5.1 Scrapy통해 복구

크롤링이 중단되었을 경우, 동일한 명령어를 재실행하면 Scrapy가 tmp/ 디렉터리의 데이터를 바탕으로 크롤링 대기열과 상태를 자동으로 복구하여 작업을 이어서 진행한다.

예. 복구하려면 아래 명령 재실행

```bash
scrapy crawl dcinside -a csv_file=data/urls.csv
```

> [!NOTE]
>
> 복구 실행의 경우에는 데이터 중간에 새 Column name행 자동으로 생성되며, 데이터 처리할 때 삭제하면 된다.


#### 5.2 row_offset 설정통해 복구

> [!IMPORTANT]
>
> Scrapy가 강제 중단되면 저장된 임시 대기열 파일이 손상될 수 있고 result.csv의 저장 진행 상황을 확인한 후, 이미 크롤링된 url.csv의 행을 row_offset을 통해 건너뛸 수 있다.

```bash
scrapy crawl dcinside -a csv_file=data/urls.csv -a row_offset=200
```

위 명령은 크롤러가 url.csv의 200 행(row index=200)부터 크롤링을 재개한다는 뜻다.

### 기타

- Author: Jmsu
- Email: huigz512@gmail.com
