import scrapy
import pandas as pd
from scrapy.loader import ItemLoader
from ..items import DcinsideScrapyItem
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import re
from time import sleep, time
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn



class DcinsideSpider(scrapy.Spider):
    name = "dcinside"

    # scrapy request settings
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': True,  
        'DOWNLOAD_DELAY_RANGE': (0.5, 1),
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,  
    }
    
    def __init__(self, csv_file=None, delay=0.7, row_offset=0, *args, **kwargs):
        super(DcinsideSpider, self).__init__(*args, **kwargs)
        self.csv_file = csv_file
        self.delay = delay
        self.row_offset = int(row_offset)
        self.console = Console()
        self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=self.console,
                refresh_per_second=2
            )
        self.task_id = None
        self.total_urls = 0
        self.processed_urls = 0
            
            
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DcinsideSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.settings.set("DOWNLOAD_DELAY", spider.delay, priority='spider')
        return spider

    def start_requests(self):
        self.console.print(f"[yellow]--------------Crawler Settings---------------[/yellow]")
        self.console.print(f"[yellow]DOWNLOAD_DELAY: [blue]{self.delay}s[/blue][/yellow]")
        self.console.print(f"[yellow]ROW_OFFSET: [blue]{self.row_offset}[/blue][/yellow]")
        self.console.print(f"[yellow]-----------------------:smile:--------------------[/yellow]")
        self.console.print(f"CRAWLER STARTING IN 5 SECONDS...", style="bold blue")
        sleep(5)
        self.console.print(f"STARTING...", style="bold green")
        
        if not self.csv_file:
            self.logger.error("[Please provide the URL CSV file path!] Use -a csv_file=your_file.csv")
            self.console.print('[red][Please provide the URL CSV file path!][/red] Use "-a csv_file=your_file.csv"')
            return
        
        try:
            df = pd.read_csv(self.csv_file)
            df.columns = df.columns.str.lower() # convert all column names to lowercase

            # row offset
            if self.row_offset > df.index.max():
                self.console.print(f"[red bold]:x:Row offset is greater than the number of rows in the CSV file![/red bold]")
            df = df.iloc[self.row_offset:]

            self.total_urls = len(df)        
            
            self.progress.start()

            self.task_id = self.progress.add_task(
                "[cyan]Crawling URLs...", 
                total=self.total_urls
            )
            
            for index, row in df.iterrows():
                url = row['url']
                parse_url = urlparse(url)
                params = parse_qs(parse_url.query)
                page = params.get('page', [''])[0]
                no = params.get('no', [''])[0]

                yield scrapy.Request(
                    url=row['url'],
                    callback=self.parse_article,
                    meta={'Artist': row['artist'], 'Date': row['date'], 'Page': page, 'No': no}
                )
                    
        except Exception as e:
            self.logger.error(f"[Error during reading the CSV file!] {str(e)}")
            self.console.print(f'[red]Error reading CSV file: {str(e)}[/red]')

    def parse_article(self, response):
        
        if self.progress:
            self.processed_urls += 1
            
            page = response.meta.get('Page', '')
            no = response.meta.get('No', '') 
            
            # 更新进度
            self.progress.update(
                self.task_id, 
                completed=self.processed_urls,
                description=f"[cyan]|Page: {page}, No: {no}| :rocket: Processing ... ({self.processed_urls}/{self.total_urls})"
            )
            
            # 强制刷新进度条显示
            self.progress.refresh()
        
        loader = ItemLoader(item=DcinsideScrapyItem(), response=response)    
    
        try:
            artist = response.meta['Artist']
            date = response.meta['Date']
        except KeyError as e:
            self.logger.error(f"[Missing required meta data!] {str(e)}")
            self.console.print(f"[red]✗ Required meta data missing [Please check the URL CSV file!]: {str(e)} [/red]")
            raise scrapy.exceptions.CloseSpider(f"Required meta data missing [Please check the URL CSV file!]: {str(e)}")
        
        # save meta data to item
        loader.add_value('artist', artist)
        loader.add_value('date', date)
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
            self.console.print(f"[green]✓ Success: {item.get('url')}[/green]")
            yield item


#------------------retry--------------------------------
        else:
            relocation_match = r"<script>location\.href\s*=\s*'([^']+)'</script>"
            match = re.search(relocation_match, response.text)
            
            if match:
                url = match.group(1)
                self.console.print(f"[yellow]↻ Redirect: {url}[/yellow]")
                self.logger.warning(f"[redirect]: URL redirect to {url}")
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_article,
                    meta={'Artist': artist, 'Date': date}
                )
            else:
                #save error html file and retry----
                parsed_url = urlparse(response.url)
                params = parse_qs(parsed_url.query)
                with open(f'debug_warning_html/{params["no"][0]}.html', 'w') as f:
                    f.write(response.text)
                
                self.console.print(f"[red]✗ Retry: {response.url}[/red]")
                self.logger.error(f"[retry]: Missing required fields for {response.url}")
                yield scrapy.Request(
                    url=response.url,
                    callback=self.parse_article,
                    meta={'Artist': artist, 'Date': date},
                    dont_filter=True
                )

    def closed(self, reason):
        if self.progress:
            self.progress.stop()
            self.console.print(f"[bold green]Crawling completed! Processed {self.processed_urls} URLs.[/bold green]")
        