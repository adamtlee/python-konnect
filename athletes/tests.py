from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO
from unittest.mock import patch, MagicMock


class OpenOneFCCommandTest(TestCase):
    """Test cases for the open_onefc management command."""

    @patch('athletes.management.commands.open_onefc.CrawlerProcess')
    def test_command_fetches_correct_url(self, mock_crawler_process):
        """Test that the command fetches the correct URL with Scrapy."""
        # Mock the CrawlerProcess
        mock_process = MagicMock()
        mock_crawler_process.return_value = mock_process
        
        out = StringIO()
        
        call_command('open_onefc', stdout=out)
        
        # Verify CrawlerProcess was instantiated
        mock_crawler_process.assert_called_once()
        
        # Verify crawl was called with the spider
        mock_process.crawl.assert_called_once()
        
        # Verify start was called
        mock_process.start.assert_called_once()
        
        # Verify output messages
        output = out.getvalue()
        self.assertIn('Fetching page with Scrapy:', output)
        self.assertIn('https://www.onefc.com/athletes/weight-class/flyweight/', output)
        self.assertIn('Page fetched successfully with Scrapy!', output)

    @patch('athletes.management.commands.open_onefc.CrawlerProcess')
    @patch('athletes.management.commands.open_onefc.webbrowser')
    def test_command_with_open_browser_option(self, mock_webbrowser, mock_crawler_process):
        """Test that the command opens browser when --open-browser flag is used."""
        mock_process = MagicMock()
        mock_crawler_process.return_value = mock_process
        
        out = StringIO()
        
        call_command('open_onefc', '--open-browser', stdout=out)
        
        # Verify browser was opened
        mock_webbrowser.open.assert_called_once_with(
            'https://www.onefc.com/athletes/weight-class/flyweight/'
        )
        
        output = out.getvalue()
        self.assertIn('Browser opened successfully!', output)

    @patch('athletes.management.commands.open_onefc.CrawlerProcess')
    def test_command_handles_scrapy_error(self, mock_crawler_process):
        """Test that the command handles Scrapy errors gracefully."""
        # Simulate CrawlerProcess raising an exception
        mock_crawler_process.side_effect = Exception("Scrapy error")
        out = StringIO()
        
        # The command should handle the error
        with self.assertRaises(Exception):
            call_command('open_onefc', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Error fetching page:', output)

    @patch('athletes.management.commands.open_onefc.CrawlerProcess')
    def test_command_output_formatting(self, mock_crawler_process):
        """Test that the command produces properly formatted output."""
        mock_process = MagicMock()
        mock_crawler_process.return_value = mock_process
        
        out = StringIO()
        
        call_command('open_onefc', stdout=out, verbosity=2)
        
        output = out.getvalue()
        # Check that success messages are present
        self.assertIn('Fetching page with Scrapy:', output)
        self.assertIn('Page fetched successfully with Scrapy!', output)
