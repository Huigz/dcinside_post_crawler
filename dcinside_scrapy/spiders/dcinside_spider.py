import scrapy
import pandas as pd
from scrapy.loader import ItemLoader
from ..items import DcinsideScrapyItem


class DcinsideSpider(scrapy.Spider):
    name = "dcinside"

    # scrapy request settings
    custom_settings = {
        'DOWNLOAD_DELAY': 1,  
        'RANDOMIZE_DOWNLOAD_DELAY': True,  
        'DOWNLOAD_DELAY_RANGE': (0.5, 1.5),
        'RETRY_TIMES': 5,     
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],  
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,  
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
        loader.add_css('nickname', '.gallview_head .gall_writer::attr(data-nick)')
        loader.add_css('ip', '.gallview_head .gall_writer::attr(data-ip)')
        loader.add_css('uid', '.gallview_head .gall_writer::attr(data-uid)')
        loader.add_value('url', response.url)
        loader.add_css('content', '.write_div *::text') # it will save as a text list
        loader.add_css('like', '.gallview_head .gall_reply_num::text')
        loader.add_css('unlike', '.down_num::text')
        loader.add_css('view', '.gallview_head .gall_count::text')
        
        yield loader.load_item() 