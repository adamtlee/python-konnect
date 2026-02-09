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
    
    def __init__(self, max_athletes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_athletes = max_athletes  # None means get all athletes

    def parse(self, response):
        """Parse the main page and extract athlete links."""
        self.logger.info(f'Successfully fetched main page: {response.url}')
        self.logger.info(f'Response status: {response.status}')
        
        # Extract athlete cards
        athlete_cards = response.css('div.simple-post-card.is-athlete')
        
        # Extract names and links from each card
        athletes_data = []
        for card in athlete_cards:
            # Extract name from h3 tag
            name = card.css('h3::text').get()
            # Extract link
            link = card.css('a::attr(href)').get()
            
            if name and link and '/athletes/' in link:
                # Clean up name (strip whitespace)
                name = name.strip()
                # Make link absolute if needed
                if not link.startswith('http'):
                    link = response.urljoin(link)
                
                athletes_data.append({'name': name, 'link': link})
        
        # Remove duplicates based on link while preserving order
        seen_links = set()
        unique_athletes = []
        for athlete in athletes_data:
            if athlete['link'] not in seen_links:
                seen_links.add(athlete['link'])
                unique_athletes.append(athlete)
        
        # Take only the first N unique athletes if limit is set, otherwise get all
        if self.max_athletes is not None:
            athletes_to_print = unique_athletes[:self.max_athletes]
        else:
            athletes_to_print = unique_athletes
        
        # Print athlete names to console
        print("\n" + "="*80)
        print(f"ALL ATHLETES FOUND ({len(athletes_to_print)} total):")
        print("="*80)
        for idx, athlete in enumerate(athletes_to_print, 1):
            print(f"{idx}. {athlete['name']}")
        print("="*80 + "\n")
        
        self.logger.info(f'Found {len(athletes_to_print)} athletes on the page')


class Command(BaseCommand):
    help = 'Scrapes all athletes from ONE Championship flyweight page using Scrapy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--open-browser',
            action='store_true',
            help='Also open the main page in the default browser',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=None,
            help='Limit number of athletes to fetch (default: all athletes)',
        )

    def handle(self, *args, **options):
        url = 'https://www.onefc.com/athletes/weight-class/flyweight/'
        athlete_count = options.get('count', None)
        
        if athlete_count:
            self.stdout.write(
                self.style.SUCCESS(f'Fetching page to find first {athlete_count} athletes: {url}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Fetching page to scrape all athletes: {url}')
            )
        
        try:
            # Configure Scrapy settings
            process = CrawlerProcess({
                'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'LOG_LEVEL': 'WARNING',  # Reduce log noise since we're printing HTML
            })
            
            # Add the spider to the process with max_athletes parameter
            process.crawl(OneFCAthletesSpider, max_athletes=athlete_count)
            
            # Start the crawling process
            process.start()
            
            if athlete_count:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully found {athlete_count} athletes on the page!')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Successfully scraped all athletes from the page!')
                )
            
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
