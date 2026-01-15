# Beautiful Soup Interface

A web-based application for scraping, processing, and analyzing web content using Beautiful Soup and Flask. Extract data from websites with an intuitive UI, download results, and integrate with webhooks.

## Features

- **Web Scraping**: Extract content from any website using Beautiful Soup
- **Content Modes**: Choose between clean text extraction or full HTML preservation
- **Image Processing**: Automatically download and save images found on pages
- **Metadata Extraction**: Pull meta tags, titles, and descriptions from web pages
- **Multiple Export Formats**:
  - Download results as JSON
  - Download processed content as ZIP files
- **Webhook Integration**: Send processed data to external services via webhooks
- **User-Friendly Interface**: Clean, responsive web UI built with Flask and Jinja2
- **Session Management**: Temporary storage for processing results with unique IDs

## Tech Stack

- **Backend**: Flask (Python)
- **Web Scraping**: Beautiful Soup 4
- **HTTP Client**: Requests
- **Templating**: Jinja2
- **Frontend**: HTML, CSS, JavaScript

## Requirements

- Python 3.8+
- See `requirements.txt` for all dependencies

### Dependencies

```
beautifulsoup4==4.13.3
Flask==3.1.0
requests==2.32.3
```

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Mehdi-Samardan/Beautiful-Soup-interface.git
   cd Beautiful-Soup-interface
   ```

2. **Create a virtual environment** (optional but recommended)

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

### Web Interface

1. **Enter URL**: Paste the website URL you want to scrape
2. **Select Content Mode**:
   - **Clean**: Extract clean text content only
   - **Full**: Preserve all HTML tags and formatting
3. **Process**: Click submit to process the URL
4. **Results**: View extracted data with options to:
   - Download as JSON
   - Send to webhook
   - Download as ZIP (if images present)

### API Endpoints

| Endpoint                      | Method    | Description                               |
| ----------------------------- | --------- | ----------------------------------------- |
| `/`                           | GET, POST | Main interface for URL processing         |
| `/send_webhook/<process_id>`  | POST      | Send processed data to configured webhook |
| `/download_json/<process_id>` | GET       | Download results as JSON file             |
| `/download_zip`               | GET       | Download processed content with images    |

## Configuration

### Webhook URL

To enable webhook functionality, update the `WEBHOOK_URL` in [app.py](app.py#L14):

```python
WEBHOOK_URL = "https://your-webhook-url-here"
```

### Headers

The application includes default browser headers to avoid being blocked by websites. Modify headers in [app.py](app.py#L26) if needed.

## Project Structure

```
├── app.py                 # Main Flask application
├── utils.py              # Utility functions for scraping
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/
│   ├── css/
│   │   └── styles.css   # Styling
│   └── js/
│       └── scripts.js   # Client-side logic
└── templates/
    ├── index.html       # Main form page
    ├── result.html      # Results display page
    └── webhook_sent.html # Webhook confirmation page
```

## Key Functions

### app.py

- `index()` - Main route for URL input and processing
- `send_webhook()` - Sends processed data to webhook endpoint
- `download_zip()` - Serves processed files as ZIP
- `download_json()` - Returns results as JSON

### utils.py

- `fetch_page()` - Fetches webpage content with error handling
- `process_images()` - Downloads and saves images from pages
- `extract_meta()` - Extracts metadata from HTML
- `process_url()` - Main processing pipeline
- `send_all_properties()` - Sends data to webhook

## Error Handling

The application includes robust error handling for:

- Invalid URLs
- Network timeouts
- Failed image downloads
- Missing process IDs
- File system errors

## Notes

- Results are stored temporarily in memory (`RESULTS` dictionary)
- Images are saved to local folders named after the source domain
- Default timeout for requests is 30 seconds
- User-Agent headers are set to mimic a browser request

## Future Improvements

- Database integration for persistent storage
- Advanced filtering and search capabilities
- Scheduled/automated scraping
- Enhanced error logging
- Rate limiting and request throttling
- Support for JavaScript-rendered content

## License

This project is open source and available under the MIT License.

## Author

[Mehdi-Samardan](https://github.com/Mehdi-Samardan)
