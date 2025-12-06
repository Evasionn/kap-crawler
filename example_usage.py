#!/usr/bin/env python3
"""Simple example usage of KAP Crawler."""

import logging
from kap import Crawler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Example usage of KAP crawler."""
    
    # Initialize crawler
    print("Initializing KAP crawler...")
    crawler = Crawler(request_delay=1.0)
    
    # Fetch fund announcements
    print("\n" + "="*60)
    print("FETCHING FUND ANNOUNCEMENTS")
    print("="*60)
    fund_announcements = crawler.fetch_fund_announcements(
        from_date="2024-12-06",
        to_date="2025-12-06",
        fund_type_list=["YF"],
        limit=15
    )
    
    if fund_announcements:
        print(f"\n✅ Found {len(fund_announcements)} fund announcement(s):\n")
        for idx, ann in enumerate(fund_announcements, 1):
            print(f"{'='*60}")
            print(f"Fund Announcement #{idx}:")
            print(f"  ID: {ann['announcement_id']}")
            print(f"  Date/Time: {ann['date_time']}")
            print(f"  Fund: {ann['fund_name']} ({ann['fund_code']})")
            print(f"  Subject: {ann['subject']}")
            print(f"  Summary: {ann['summary']}")
            print(f"  Related Stocks: {ann['related_stocks']}")
            print(f"  Has Attachment: {ann['has_attachment']} (Count: {ann['attachment_count']})")
            print(f"  Detail PDF URL: {ann['detail_pdf_url']}")
            if ann['attachment_pdf_url']:
                print(f"  Attachment PDF URL: {ann['attachment_pdf_url']}")
            print()
    else:
        print("\n❌ No fund announcements found")
    
    # Fetch company announcements
    print("\n" + "="*60)
    print("FETCHING COMPANY ANNOUNCEMENTS")
    print("="*60)
    company_announcements = crawler.fetch_company_announcements(
        from_date="2024-12-06",
        to_date="2025-12-06",
        member_type="IGS",
        limit=5
    )
    
    if company_announcements:
        print(f"\n✅ Found {len(company_announcements)} company announcement(s):\n")
        for idx, ann in enumerate(company_announcements, 1):
            print(f"{'='*60}")
            print(f"Company Announcement #{idx}:")
            print(f"  ID: {ann['announcement_id']}")
            print(f"  Date/Time: {ann['date_time']}")
            print(f"  Company: {ann['company_name']} ({ann['company_code']})")
            print(f"  Subject: {ann['subject']}")
            print(f"  Summary: {ann['summary']}")
            print(f"  Related Companies: {ann['related_companies']}")
            print(f"  Has Attachment: {ann['has_attachment']} (Count: {ann['attachment_count']})")
            print(f"  Detail PDF URL: {ann['detail_pdf_url']}")
            if ann['attachment_pdf_url']:
                print(f"  Attachment PDF URL: {ann['attachment_pdf_url']}")
            print()
    else:
        print("\n❌ No company announcements found")

if __name__ == "__main__":
    main()
