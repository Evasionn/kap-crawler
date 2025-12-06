# KAP Crawler

Simple and efficient crawler for fetching announcements from [Kamuyu Aydınlatma Platformu (KAP)](https://www.kap.org.tr).

## Features

- ✅ Fetch fund announcements from KAP API (`/tr/api/disclosure/funds/byCriteria`)
- ✅ Fetch company announcements from KAP API (`/tr/api/disclosure/members/byCriteria`)
- ✅ Extract announcement details: ID, date/time, fund/company info, subject, summary
- ✅ Get detail PDF URL (`/tr/api/BildirimPdf/{id}`)
- ✅ Fetch attachment PDF URLs when available

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Fetch Fund Announcements

```python
from kap import Crawler

crawler = Crawler(request_delay=1.0)

# Fetch fund announcements
fund_announcements = crawler.fetch_fund_announcements(
    from_date="2024-12-06",
    to_date="2025-12-06",
    fund_type_list=["YF"],  # Yatırım Fonları
    limit=15
)

for ann in fund_announcements:
    print(f"Fund: {ann['fund_name']} ({ann['fund_code']})")
    print(f"Subject: {ann['subject']}")
    print(f"Detail PDF: {ann['detail_pdf_url']}")
    if ann['attachment_pdf_url']:
        print(f"Attachment PDF: {ann['attachment_pdf_url']}")
```

### Fetch Company Announcements

```python
# Fetch company announcements
company_announcements = crawler.fetch_company_announcements(
    from_date="2024-12-06",
    to_date="2025-12-06",
    member_type="IGS",  # İşletmeler Genel Sınıfı
    limit=10
)

for ann in company_announcements:
    print(f"Company: {ann['company_name']} ({ann['company_code']})")
    print(f"Subject: {ann['subject']}")
    print(f"Detail PDF: {ann['detail_pdf_url']}")
```

## Data Structure

### Fund Announcement

- `announcement_id`: Numeric announcement ID (e.g., "1524023")
- `date_time`: Publication date and time (e.g., "05.12.2025 22:17:35")
- `fund_code`: Fund code (e.g., "PDF")
- `fund_name`: Full fund name
- `subject`: Announcement subject
- `summary`: Summary text
- `related_stocks`: List of related stock codes
- `has_attachment`: Boolean indicating if attachment exists
- `attachment_count`: Number of attachments
- `detail_pdf_url`: URL to detail PDF (`/tr/api/BildirimPdf/{id}`)
- `attachment_pdf_url`: URL to attachment PDF (if available, `None` otherwise)

### Company Announcement

- `announcement_id`: Numeric announcement ID
- `date_time`: Publication date and time
- `company_code`: Stock code (e.g., "ALFAS")
- `company_name`: Full company name
- `subject`: Announcement title/subject
- `summary`: Summary text
- `related_companies`: List of related company codes
- `has_attachment`: Boolean indicating if attachment exists
- `attachment_count`: Number of attachments
- `detail_pdf_url`: URL to detail PDF (`/tr/api/BildirimPdf/{id}`)
- `attachment_pdf_url`: URL to attachment PDF (if available, `None` otherwise)

## API Reference

### `Crawler(request_delay=1.0, timeout=30)`

Initialize the crawler.

**Parameters:**
- `request_delay`: Delay between requests in seconds (default: 1.0)
- `timeout`: Request timeout in seconds (default: 30)

### `fetch_fund_announcements(from_date=None, to_date=None, fund_type_list=None, limit=None)`

Fetch fund announcements from KAP.

**Parameters:**
- `from_date`: Start date in YYYY-MM-DD format (default: 30 days ago)
- `to_date`: End date in YYYY-MM-DD format (default: today)
- `fund_type_list`: List of fund types (e.g., `["YF"]`, `["BYF"]`, etc.) (default: `["YF"]`)
- `limit`: Maximum number of announcements to return (None = all)

**Returns:**
- List of fund announcement dictionaries

### `fetch_company_announcements(from_date=None, to_date=None, member_type="IGS", limit=None)`

Fetch company announcements from KAP.

**Parameters:**
- `from_date`: Start date in YYYY-MM-DD format (default: 30 days ago)
- `to_date`: End date in YYYY-MM-DD format (default: today)
- `member_type`: Member type (default: "IGS" - İşlem Gören Şirketler)
- `limit`: Maximum number of announcements to return (None = all)

**Returns:**
- List of company announcement dictionaries

## How It Works

1. **Fund Announcements**: Uses `/tr/api/disclosure/funds/byCriteria` endpoint
2. **Company Announcements**: Uses `/tr/api/disclosure/members/byCriteria` endpoint
3. **Extracts data**: Parses API response to get announcement details
4. **Gets detail PDF URL**: Constructs `/tr/api/BildirimPdf/{id}` URL
5. **Fetches attachments**: If `attachmentCount > 0`, scrapes detail page to find PDF download URL

## Requirements

- Python 3.7+
- `requests` - HTTP library
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser

## License

MIT
