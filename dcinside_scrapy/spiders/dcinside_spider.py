import scrapy
import pandas as pd
from scrapy.loader import ItemLoader
from ..items import DcinsideScrapyItem


class DcinsideSpider(scrapy.Spider):
    name = "dcinside"
#    allowed_domains = ["dcinside.com"]
    
    # 设置请求延迟和重试
    custom_settings = {
        'DOWNLOAD_DELAY': 1,  
        'RETRY_TIMES': 3,     
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],  
    }
    
    def __init__(self, csv_file=None, *args, **kwargs):
        super(DcinsideSpider, self).__init__(*args, **kwargs)
        self.csv_file = csv_file
        if not self.csv_file:
            self.logger.error("[Please provide the URL CSV file path!] Use -a csv_file=your_file.csv")
            return

    def start_requests(self):
        try:
            df = pd.read_csv(self.csv_file)
            for index, row in df.iterrows():
                yield scrapy.Request(
                    url=row['Url'],
                    callback=self.parse_article,
                    meta={'Artist': row['Artist'], 'Month': row['Month']}
                )
        except Exception as e:
            self.logger.error(f"[Error during reading the CSV file!] {str(e)}")


    def parse_article(self, response):
    
        loader = ItemLoader(item=DcinsideScrapyItem(), response=response)    
    
        try:
            artist = response.meta['Artist']
            month = response.meta['Month']
        except KeyError as e:
            self.logger.error(f"[Missing required meta data!] {str(e)}")
            raise scrapy.exceptions.CloseSpider(f"Required meta data missing [Please check the URL CSV file!]: {str(e)}")
        
        # save meta data to item

        loader.add_value('artist', artist)
        loader.add_value('month', month)
        
        # save data from web page to item
        
        nickname = response.css(".nickname").attrib.get('title')
        ip = response.css(".ip::text").get()
        
    
        loader.add_css('title', '.title_subject::text')
        loader.add_css('nickname', '.nickname::attr(title)')
        loader.add_css('ip', '.ip::text')
        loader.add_value('url', response.url)
        loader.add_css('content', '.write_div *::text') # it will save as a text list
        loader.add_css('like', '.gallview_head .gall_reply_num::text')
        loader.add_css('unlike', '.gallview_head .down_num::text')
        loader.add_css('view', '.gallview_head .gall_count::text')
        
        yield loader.load_item() 