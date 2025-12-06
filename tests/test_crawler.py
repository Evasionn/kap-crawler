"""Tests for KAP crawler."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from kap import Crawler


class TestCrawler:
    """Test cases for Crawler class."""
    
    def test_crawler_initialization(self):
        """Test crawler initialization."""
        crawler = Crawler(request_delay=1.0, timeout=30)
        assert crawler.request_delay == 1.0
        assert crawler.timeout == 30
        assert crawler.session is not None
        assert crawler.root_url == "https://www.kap.org.tr"
    
    @patch('kap.crawler.Crawler.session')
    def test_fetch_fund_announcements(self, mock_session):
        """Test fetching fund announcements."""
        # Mock API response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = [
            {
                "publishDate": "05.12.2025 22:17:35",
                "fundCode": "PDF",
                "kapTitle": "TEST FUND",
                "summary": "Test summary",
                "subject": "Test subject",
                "disclosureIndex": 1524023,
                "relatedStocks": None,
                "attachmentCount": 0
            }
        ]
        mock_session.post.return_value = mock_response
        
        crawler = Crawler()
        announcements = crawler.fetch_fund_announcements(
            from_date="2024-12-06",
            to_date="2025-12-06",
            limit=1
        )
        
        assert isinstance(announcements, list)
        if announcements:
            assert announcements[0]['fund_code'] == "PDF"
            assert announcements[0]['announcement_id'] == "1524023"
    
    @patch('kap.crawler.Crawler.session')
    def test_fetch_company_announcements(self, mock_session):
        """Test fetching company announcements."""
        # Mock API response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = [
            {
                "publishDate": "06.12.2025 14:29:07",
                "kapTitle": "TEST COMPANY A.Ş.",
                "stockCodes": "TEST",
                "summary": "Test summary",
                "subject": "Test subject",
                "disclosureIndex": 1524033,
                "relatedStocks": None,
                "attachmentCount": 0
            }
        ]
        mock_session.post.return_value = mock_response
        
        crawler = Crawler()
        announcements = crawler.fetch_company_announcements(
            from_date="2024-12-06",
            to_date="2025-12-06",
            limit=1
        )
        
        assert isinstance(announcements, list)
        if announcements:
            assert announcements[0]['company_code'] == "TEST"
            assert announcements[0]['announcement_id'] == "1524033"
    
    def test_extract_fund_announcement(self):
        """Test fund announcement extraction."""
        crawler = Crawler()
        item = {
            "publishDate": "05.12.2025 22:17:35",
            "fundCode": "PDF",
            "kapTitle": "TEST FUND",
            "summary": "Test summary",
            "subject": "Test subject",
            "disclosureIndex": 1524023,
            "relatedStocks": None,
            "attachmentCount": 0
        }
        
        ann = crawler._extract_fund_announcement(item)
        assert ann is not None
        assert ann['fund_code'] == "PDF"
        assert ann['fund_name'] == "TEST FUND"
        assert ann['announcement_id'] == "1524023"
        assert ann['has_attachment'] is False
    
    def test_extract_company_announcement(self):
        """Test company announcement extraction."""
        crawler = Crawler()
        item = {
            "publishDate": "06.12.2025 14:29:07",
            "kapTitle": "TEST COMPANY A.Ş.",
            "stockCodes": "TEST",
            "summary": "Test summary",
            "subject": "Test subject",
            "disclosureIndex": 1524033,
            "relatedStocks": None,
            "attachmentCount": 0
        }
        
        ann = crawler._extract_company_announcement(item)
        assert ann is not None
        assert ann['company_code'] == "TEST"
        assert ann['company_name'] == "TEST COMPANY A.Ş."
        assert ann['announcement_id'] == "1524033"
        assert ann['has_attachment'] is False
