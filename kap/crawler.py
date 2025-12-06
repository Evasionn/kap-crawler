"""KAP Crawler - Simple and efficient announcement scraper."""

import logging
import re
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Crawler:
    """Simple KAP announcement crawler.
    
    Fetches announcements from KAP API for both companies and funds.
    """
    
    root_url = "https://www.kap.org.tr"
    
    def __init__(self, request_delay: float = 1.0, timeout: int = 30):
        """Initialize crawler.
        
        Args:
            request_delay: Delay between requests in seconds (default: 1.0)
            timeout: Request timeout in seconds (default: 30)
        """
        self.request_delay = request_delay
        self.timeout = timeout
        self.last_request_time = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Referer": "https://www.kap.org.tr/tr",
        })
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()
    
    def fetch_fund_announcements(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        fund_type_list: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Fetch fund announcements from KAP API.
        
        Args:
            from_date: Start date in YYYY-MM-DD format (default: 30 days ago)
            to_date: End date in YYYY-MM-DD format (default: today)
            fund_type_list: List of fund types (e.g., ["YF"], ["BYF"], etc.)
            limit: Maximum number of announcements to return (None = all)
        
        Returns:
            List of fund announcement dictionaries
        """
        self._enforce_rate_limit()
        
        # Set default dates if not provided
        if to_date is None:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if from_date is None:
            from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        if fund_type_list is None:
            fund_type_list = ["YF"]  # Default to Yatırım Fonları
        
        api_url = f"{self.root_url}/tr/api/disclosure/funds/byCriteria"
        
        payload = {
            "fromDate": from_date,
            "toDate": to_date,
            "fundTypeList": fund_type_list,
            "mkkMemberOidList": [],
            "fundOidList": [],
            "passiveFundOidList": [],
            "disclosureClass": "",
            "isLate": "",
            "subjectList": [],
            "discIndex": [],
            "fromSrc": False,
            "srcCategory": ""
        }
        
        try:
            response = self.session.post(
                api_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.ok:
                data = response.json()
                if isinstance(data, list):
                    announcements = self._parse_fund_announcements(data, limit)
                    logger.info(f"Fetched {len(announcements)} fund announcements from API")
                    return announcements
                else:
                    logger.warning(f"Unexpected API response format: {type(data)}")
            else:
                logger.error(f"API request failed with status {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching fund announcements: {e}")
        
        return []
    
    def _parse_fund_announcements(self, data: list, limit: Optional[int]) -> List[Dict]:
        """Parse fund announcement API response.
        
        Args:
            data: API response JSON (list of items)
            limit: Maximum number of announcements to return
        
        Returns:
            List of fund announcement dictionaries
        """
        announcements = []
        
        items = data[:limit] if limit else data
        
        for item in items:
            ann = self._extract_fund_announcement(item)
            if ann:
                announcements.append(ann)
        
        return announcements
    
    def _extract_fund_announcement(self, item: dict) -> Optional[Dict]:
        """Extract fund announcement data from API item.
        
        Args:
            item: API response item
        
        Returns:
            Fund announcement dictionary or None
        """
        try:
            disclosure_index = item.get("disclosureIndex")
            if not disclosure_index:
                return None
            
            # Get detail PDF URL
            detail_pdf_url = f"{self.root_url}/tr/api/BildirimPdf/{disclosure_index}"
            
            # Check for attachments
            attachment_count = item.get("attachmentCount", 0)
            has_attachment = attachment_count > 0
            attachment_pdf_url = None
            
            if has_attachment:
                # Fetch attachment URL from detail page
                attachment_pdf_url = self._fetch_attachment_url(str(disclosure_index))
            
            # Extract related stocks
            related_stocks = item.get("relatedStocks")
            related_companies = []
            if related_stocks:
                if isinstance(related_stocks, list):
                    related_companies = related_stocks
                elif isinstance(related_stocks, str):
                    related_companies = [related_stocks]
            
            announcement = {
                "announcement_id": str(disclosure_index),
                "date_time": item.get("publishDate"),
                "fund_code": item.get("fundCode"),
                "fund_name": item.get("kapTitle"),
                "subject": item.get("subject"),
                "summary": item.get("summary"),
                "related_stocks": related_companies,
                "has_attachment": has_attachment,
                "attachment_count": attachment_count,
                "detail_pdf_url": detail_pdf_url,
                "attachment_pdf_url": attachment_pdf_url,
            }
            
            return announcement
            
        except Exception as e:
            logger.error(f"Error extracting fund announcement from API item: {e}")
            return None
    
    def fetch_company_announcements(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        member_type: str = "IGS",
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Fetch company announcements from KAP API.
        
        Args:
            from_date: Start date in YYYY-MM-DD format (default: 30 days ago)
            to_date: End date in YYYY-MM-DD format (default: today)
            member_type: Member type (default: "IGS" - İşletmeler Genel Sınıfı)
            limit: Maximum number of announcements to return (None = all)
        
        Returns:
            List of company announcement dictionaries
        """
        self._enforce_rate_limit()
        
        # Set default dates if not provided
        if to_date is None:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if from_date is None:
            from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        api_url = f"{self.root_url}/tr/api/disclosure/members/byCriteria"
        
        payload = {
            "fromDate": from_date,
            "toDate": to_date,
            "memberType": member_type,
            "mkkMemberOidList": [],
            "inactiveMkkMemberOidList": [],
            "disclosureClass": "",
            "subjectList": [],
            "isLate": "",
            "mainSector": "",
            "sector": "",
            "subSector": "",
            "marketOid": "",
            "index": "",
            "bdkReview": "",
            "bdkMemberOidList": [],
            "year": "",
            "term": "",
            "ruleType": "",
            "period": "",
            "fromSrc": False,
            "srcCategory": "",
            "disclosureIndexList": []
        }
        
        try:
            response = self.session.post(
                api_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.ok:
                data = response.json()
                if isinstance(data, list):
                    announcements = self._parse_company_announcements(data, limit)
                    logger.info(f"Fetched {len(announcements)} company announcements from API")
                    return announcements
                else:
                    logger.warning(f"Unexpected API response format: {type(data)}")
            else:
                logger.error(f"API request failed with status {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching company announcements: {e}")
        
        return []
    
    def _parse_company_announcements(self, data: list, limit: Optional[int]) -> List[Dict]:
        """Parse company announcement API response.
        
        Args:
            data: API response JSON (list of items)
            limit: Maximum number of announcements to return
        
        Returns:
            List of announcement dictionaries
        """
        announcements = []
        
        items = data[:limit] if limit else data
        
        for item in items:
            ann = self._extract_company_announcement(item)
            if ann:
                announcements.append(ann)
        
        return announcements
    
    def _extract_company_announcement(self, item: dict) -> Optional[Dict]:
        """Extract company announcement data from API item.
        
        Args:
            item: API response item
        
        Returns:
            Announcement dictionary or None
        """
        try:
            disclosure_index = item.get("disclosureIndex")
            if not disclosure_index:
                return None
            
            # Get detail PDF URL
            detail_pdf_url = f"{self.root_url}/tr/api/BildirimPdf/{disclosure_index}"
            
            # Check for attachments
            attachment_count = item.get("attachmentCount", 0)
            has_attachment = attachment_count > 0
            attachment_pdf_url = None
            
            if has_attachment:
                # Fetch attachment URL from detail page
                attachment_pdf_url = self._fetch_attachment_url(str(disclosure_index))
            
            # Extract company code from stockCodes (string field)
            stock_codes = item.get("stockCodes")
            company_code = None
            if stock_codes:
                # stockCodes is a string, might be comma-separated
                if isinstance(stock_codes, str):
                    # Take first code if multiple
                    company_code = stock_codes.split(",")[0].strip()
                else:
                    company_code = str(stock_codes)
            
            # Extract related companies from relatedStocks
            related_stocks = item.get("relatedStocks")
            related_companies = []
            if related_stocks:
                if isinstance(related_stocks, list):
                    related_companies = related_stocks
                elif isinstance(related_stocks, str):
                    related_companies = [related_stocks]
            
            announcement = {
                "announcement_id": str(disclosure_index),
                "date_time": item.get("publishDate"),
                "company_code": company_code,
                "company_name": item.get("kapTitle"),
                "subject": item.get("subject"),
                "summary": item.get("summary"),
                "related_companies": related_companies,
                "has_attachment": has_attachment,
                "attachment_count": attachment_count,
                "detail_pdf_url": detail_pdf_url,
                "attachment_pdf_url": attachment_pdf_url,
            }
            
            return announcement
            
        except Exception as e:
            logger.error(f"Error extracting company announcement from API item: {e}")
            return None
    
    def _fetch_attachment_url(self, announcement_id: str) -> Optional[str]:
        """Fetch PDF attachment URL from announcement detail page.
        
        Args:
            announcement_id: Announcement ID (numeric, e.g., "1524030")
        
        Returns:
            PDF attachment URL or None
        """
        self._enforce_rate_limit()
        
        url = f"{self.root_url}/tr/Bildirim/{announcement_id}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find "Bildirim Ekleri" section - look for text containing this
            # The section usually has a heading or label with "Bildirim Ekleri"
            attachment_text = soup.find(string=re.compile(r'Bildirim Ekleri', re.I))
            if attachment_text:
                # Find parent container
                parent = attachment_text.find_parent()
                # Navigate up to find the container with links
                while parent:
                    # Look for download links in this parent and its children
                    links = parent.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        # Check if it's a download link
                        if '/api/file/download/' in href:
                            # Make absolute URL
                            if not href.startswith('http'):
                                href = urljoin(self.root_url, href)
                            logger.info(f"Found attachment PDF URL: {href}")
                            return href
                    # Try parent's parent
                    parent = parent.find_parent()
            
            # Alternative: search entire page for download links (more aggressive)
            # Also check for data attributes or script tags that might contain URLs
            download_links = soup.find_all('a', href=re.compile(r'/api/file/download/'))
            if download_links:
                href = download_links[0].get('href', '')
                if not href.startswith('http'):
                    href = urljoin(self.root_url, href)
                logger.info(f"Found attachment PDF URL (alternative search): {href}")
                return href
            
            # Last resort: search in raw HTML for download URLs
            html_text = response.text
            download_match = re.search(r'/api/file/download/[a-zA-Z0-9]+', html_text)
            if download_match:
                href = download_match.group(0)
                if not href.startswith('http'):
                    href = urljoin(self.root_url, href)
                logger.info(f"Found attachment PDF URL (regex search): {href}")
                return href
            
            logger.debug(f"No attachment found for announcement {announcement_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching attachment URL for {announcement_id}: {e}")
            return None
