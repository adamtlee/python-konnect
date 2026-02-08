"""
Django management command to fetch ONE Championship athletes page using Scrapy.
"""
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider


class OneFCAthletesSpider(Spider):
    """Scrapy spider to fetch ONE Championship athletes page."""
    name = 'onefc_athletes'
    start_urls = ['https://www.onefc.com/athletes/weight-class/flyweight/']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.html_content = None

    def parse(self, response):
        """Parse the response and extract information."""
        self.logger.info(f'Successfully fetched: {response.url}')
        self.logger.info(f'Response status: {response.status}')
        self.logger.info(f'Page title: {response.css("title::text").get()}')
        
        # Store HTML content
        self.html_content = response.text
        
        # Output HTML to console
        print("\n" + "="*80)
        print("HTML CONTENT:")
        print("="*80)
        print(self.html_content)
        print("="*80 + "\n")
        
        # You can add parsing logic here to extract athlete data
        # For example:
        # athletes = response.css('.athlete-card')
        # for athlete in athletes:
        #     yield {
        #         'name': athlete.css('.name::text').get(),
        #         'country': athlete.css('.country::text').get(),
        #     }
        
        return {
            'url': response.url,
            'status': response.status,
            'title': response.css('title::text').get(),
        }


class Command(BaseCommand):
    help = 'Fetches the ONE Championship flyweight athletes page using Scrapy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--open-browser',
            action='store_true',
            help='Also open the page in the default browser',
        )

    def handle(self, *args, **options):
        url = 'https://www.onefc.com/athletes/weight-class/flyweight/'
        
        self.stdout.write(
            self.style.SUCCESS(f'Fetching page with Scrapy: {url}')
        )
        
        try:
            # Configure Scrapy settings
            process = CrawlerProcess({
                'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'LOG_LEVEL': 'WARNING',  # Reduce log noise since we're printing HTML
            })
            
            # Add the spider to the process (Scrapy will instantiate it)
            process.crawl(OneFCAthletesSpider)
            
            # Start the crawling process
            process.start()
            
            self.stdout.write(
                self.style.SUCCESS('Page fetched successfully with Scrapy!')
            )
            
            # HTML has already been printed in the parse method
            
            # Optionally open in browser if requested
            if options['open_browser']:
                import webbrowser
                webbrowser.open(url)
                self.stdout.write(
                    self.style.SUCCESS('Browser opened successfully!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching page: {str(e)}')
            )
            raise
