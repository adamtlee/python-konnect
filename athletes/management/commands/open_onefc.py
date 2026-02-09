"""
Django management command to fetch ONE Championship athletes page using Scrapy.
"""
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from athletes.models import Athlete

# Shared data storage for spider results
spider_results = {'athletes_data': []}


class OneFCAthletesSpider(Spider):
    """Scrapy spider to fetch ONE Championship athletes page."""
    name = 'onefc_athletes'
    start_urls = ['https://www.onefc.com/athletes/weight-class/flyweight/']
    
    def __init__(self, max_athletes=None, create_records=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_athletes = max_athletes  # None means get all athletes
        self.create_records = create_records
        self.athletes_data = []

    def parse_name(self, full_name):
        """Parse full name into first_name and last_name."""
        if not full_name:
            return None, None
        
        # Clean up the name
        full_name = full_name.strip()
        
        # Split by spaces
        name_parts = full_name.split()
        
        if len(name_parts) == 0:
            return None, None
        elif len(name_parts) == 1:
            # Only one name, treat as last name
            return '', name_parts[0]
        else:
            # First part is first name, last part is last name
            # Everything in between is ignored (could be middle names)
            first_name = name_parts[0]
            last_name = name_parts[-1]
            return first_name, last_name

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
                
                # Parse name into first and last
                first_name, last_name = self.parse_name(name)
                
                if first_name is not None and last_name is not None:
                    athletes_data.append({
                        'name': name,
                        'first_name': first_name,
                        'last_name': last_name,
                        'link': link
                    })
        
        # Remove duplicates based on link while preserving order
        seen_links = set()
        unique_athletes = []
        for athlete in athletes_data:
            if athlete['link'] not in seen_links:
                seen_links.add(athlete['link'])
                unique_athletes.append(athlete)
        
        # Take only the first N unique athletes if limit is set, otherwise get all
        if self.max_athletes is not None:
            athletes_to_process = unique_athletes[:self.max_athletes]
        else:
            athletes_to_process = unique_athletes
        
        # Store for later use (shared with command)
        spider_results['athletes_data'] = athletes_to_process
        
        # Print athlete names to console
        print("\n" + "="*80)
        print(f"ALL ATHLETES FOUND ({len(athletes_to_process)} total):")
        print("="*80)
        for idx, athlete in enumerate(athletes_to_process, 1):
            print(f"{idx}. {athlete['name']} -> {athlete['first_name']} {athlete['last_name']}")
        print("="*80 + "\n")
        
        self.logger.info(f'Found {len(athletes_to_process)} athletes on the page')


class Command(BaseCommand):
    help = 'Scrapes all athletes from ONE Championship flyweight page using Scrapy and creates database records'

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
        parser.add_argument(
            '--no-create',
            action='store_true',
            help='Do not create database records (only scrape and print)',
        )

    def create_athlete_records(self, athletes_data):
        """Create athlete records in the database."""
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        self.stdout.write(
            self.style.SUCCESS(f'\nCreating database records for {len(athletes_data)} athletes...')
        )
        
        for athlete in athletes_data:
            try:
                # Check if athlete already exists (by first_name, last_name, and organization)
                existing = Athlete.objects.filter(
                    first_name=athlete['first_name'],
                    last_name=athlete['last_name'],
                    organization='ONE Championship'
                ).first()
                
                if existing:
                    self.stdout.write(
                        self.style.WARNING(f"  Skipped: {athlete['name']} (already exists)")
                    )
                    skipped_count += 1
                else:
                    # Create new athlete record
                    Athlete.objects.create(
                        organization='ONE Championship',
                        first_name=athlete['first_name'],
                        last_name=athlete['last_name'],
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"  Created: {athlete['name']}")
                    )
                    created_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  Error creating {athlete['name']}: {str(e)}")
                )
                error_count += 1
        
        # Print summary
        print("\n" + "="*80)
        print("DATABASE RECORDS SUMMARY:")
        print("="*80)
        print(f"Created: {created_count}")
        print(f"Skipped (already exist): {skipped_count}")
        print(f"Errors: {error_count}")
        print(f"Total processed: {len(athletes_data)}")
        print("="*80 + "\n")

    def handle(self, *args, **options):
        url = 'https://www.onefc.com/athletes/weight-class/flyweight/'
        athlete_count = options.get('count', None)
        create_records = not options.get('no_create', False)
        
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
            
            # Clear previous results
            spider_results['athletes_data'] = []
            
            # Add the spider to the process
            process.crawl(OneFCAthletesSpider, max_athletes=athlete_count, create_records=create_records)
            
            # Start the crawling process
            process.start()
            
            # After scraping, create database records if requested
            athletes_data = spider_results.get('athletes_data', [])
            if create_records and athletes_data:
                self.create_athlete_records(athletes_data)
            
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
