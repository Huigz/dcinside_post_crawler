import scrapy
import pandas as pd
from scrapy.loader import ItemLoader
from ..items import DcinsideScrapyItem
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import re


class DcinsideSpider(scrapy.Spider):
    name = "dcinside"

    # scrapy request settings
    custom_settings = {
        'DOWNLOAD_DELAY': 2.3, 
        'DOWNLOAD_TIMEOUT': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': True,  
        'DOWNLOAD_DELAY_RANGE': (0.5, 1),
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,  
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
        loader.add_value('url', response.url)
        
        # save data from web page to item
        loader.add_css('title', '.title_subject::text')
        loader.add_css('nickname', '.gallview_head .gall_writer::attr(data-nick)')
        loader.add_css('ip', '.gallview_head .gall_writer::attr(data-ip)')
        loader.add_css('uid', '.gallview_head .gall_writer::attr(data-uid)')
        loader.add_css('content', '.write_div *::text') # it will save as a text list
        loader.add_css('like', '.gallview_head .gall_reply_num::text')
        loader.add_css('unlike', '.down_num::text')
        loader.add_css('view', '.gallview_head .gall_count::text')
        
        item = loader.load_item()
        
            
        if item.get('title') and (item.get('nickname') or item.get('uid')):
            yield item

            
#------------------retry--------------------------------
        else:
            relocation_match = r"<script>location\.href\s*=\s*'([^']+)'</script>"
            match = re.search(relocation_match, response.text)
            
            if match:
                url = match.group(1)
                self.logger.warning(f"[redirect]: URL redirect to {url}")
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_article,
                    meta={'Artist': artist, 'Month': month}
                )
            else:
                #save error html file and retry----
                parsed_url = urlparse(response.url)
                params = parse_qs(parsed_url.query)
                with open('debug_warning_html/{}.html'.format(params['no'][0]), 'w') as f:
                    f.write(response.text)
                
                self.logger.error(f"[retry]: Missing required fields for {response.url}") #retry
                yield scrapy.Request(
                    url=response.url,
                    callback=self.parse_article,
                    meta={'Artist': artist, 'Month': month},
                    dont_filter=True
                )
            #--------------------------------
            
        