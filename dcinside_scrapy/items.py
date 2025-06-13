# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from itemloaders.processors import MapCompose, Join, TakeFirst #for scrapy 2.11.2
    

def extract_int(text):
    if text is None:
        return 0
    match = re.search(r'\d+', str(text))
    return int(match.group()) if match else 0


def clean_content(text):
    if text is None:
        return ""
    
    text = re.sub(r'[^\uAC00-\uD7A3\u3130-\u318F\u1100-\u11FF\u0020\u0041-\u005A\u0061-\u007A]', '', text)    
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()






class DcinsideScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    artist: str = scrapy.Field(
        serializer=str,
        output_processor=TakeFirst()
    )  # 아티스트 이름
    month: str = scrapy.Field(
        serializer=str,
        output_processor=TakeFirst()
    )   # Month
    url: str = scrapy.Field(
        serializer=str,
        output_processor=TakeFirst()
    )     # 게시글 URL
    nickname: str = scrapy.Field(
        serializer=str,
        output_processor=TakeFirst()
    )  # 작성자
    ip: str = scrapy.Field(
        serializer=str,
        output_processor=TakeFirst()
    )  # 작성자 ip
    uid: str = scrapy.Field(
        serializer=str,
        output_processor=TakeFirst()
    )  # 작성자 uid 
    post_id: str = scrapy.Field(
        serializer=str,
        output_processor=TakeFirst()
    )  # 게시글 ID
    title: str = scrapy.Field(
        serializer=str,
        output_processor=TakeFirst()
    )   # 게시글 제목
    like: int = scrapy.Field(
        serializer=int,
        input_processor=MapCompose(extract_int),
        output_processor=TakeFirst()
    )
    unlike: int = scrapy.Field(
        serializer=int,
        input_processor=MapCompose(extract_int),
        output_processor=TakeFirst()
    )
    view: int = scrapy.Field(
        serializer=int,
        input_processor=MapCompose(extract_int),
        output_processor=TakeFirst()
    )
    content: str = scrapy.Field(
        serializer=str,
        input_processor=MapCompose(clean_content),
        output_processor=Join(' ')
    ) # 게시글 내용
