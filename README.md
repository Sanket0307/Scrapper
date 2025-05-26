# Scrapper
# RERA Odisha Project Scraper

A Python web scraper that extracts detailed information about the first 6 registered projects from the RERA Odisha portal.

## 📋 Overview

This scraper automates the process of collecting project data from [RERA Odisha](https://rera.odisha.gov.in/projects/project-list) by clicking through "View Details" buttons and extracting structured information from project modals.

## 🎯 Features

- **Automated Modal Navigation**: Clicks "View Details" buttons and handles JavaScript-based modals
- **Comprehensive Data Extraction**: Extracts 5 key fields for each project
- **Tab Navigation**: Automatically clicks "Promoter Details" tabs when available
- **Robust Error Handling**: Continues processing even if individual projects fail
- **Clean Data Output**: Formats and displays extracted data in a structured manner

## 📊 Extracted Data Fields

For each project, the scraper extracts:

1. **RERA Regd. No** - Registration number (e.g., RP/12/2023/12345)
2. **Project Name** - Full project title
3. **Promoter Name** - Company/Developer name
4. **Address of the Promoter** - Registered office address
5. **GST No** - GST registration number

## 🛠️ Installation

### Prerequisites

- Python 3.7 or higher
- Chrome browser installed

### Install Dependencies

```bash
pip install requests beautifulsoup4 selenium webdriver-manager
```

## 🚀 Usage

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rera-odisha-scraper.git
   cd rera-odisha-scraper
   ```

2. **Run the scraper**
   ```bash
   python scraper.py
   ```

3. **View results**
   The scraper will display progress for each project and show final results:
   ```
   === RERA ODISHA PROJECT SCRAPER ===
   Scraping FIRST 6 projects exactly as requested...
   
   PROCESSING PROJECT 1/6
   ====================================
   Found Project Name: Sample Project Name
   Found RERA No: RP/12/2023/12345
   ...
   ```

## 📁 Project Structure

```
rera-odisha-scraper/
│
├── scraper.py              # Main scraper script
├── README.md              # This file
├── requirements.txt       # Python dependencies
└── .gitignore            # Git ignore file
```

## 🔧 How It Works

1. **Page Navigation**: Loads the RERA Odisha project list page
2. **Button Detection**: Finds all "View Details" buttons on the page
3. **Sequential Processing**: For each of the first 6 projects:
   - Returns to main page
   - Clicks the specific "View Details" button
   - Waits for modal to load
   - Extracts project information
   - Clicks "Promoter Details" tab if available
   - Extracts promoter information
   - Closes modal and continues

## 🎛️ Configuration

### Selenium Options
The scraper runs in headless mode by default. To see the browser in action, comment out this line in `setup_selenium_driver()`:
```python
# options.add_argument('--headless')
```

### Wait Times
Adjust wait times if you have a slower internet connection:
```python
time.sleep(8)  # Increase for slower connections
```

## 📋 Sample Output

```
============================================================
FINAL SCRAPED DATA - FIRST 6 PROJECTS
============================================================

------------------------------------------------------------
PROJECT 1
------------------------------------------------------------
Rera Regd. No: RP/12/2023/12345
Project Name: Sample Residential Complex
Promoter Name: M/S. SAMPLE DEVELOPERS PVT. LTD
Address of the Promoter: 123 Main Street, Bhubaneswar, Odisha - 751001
GST No: 21ABCDE1234F1Z5

------------------------------------------------------------
PROJECT 2
------------------------------------------------------------
...
```

## 🚨 Error Handling

The scraper includes comprehensive error handling:

- **Stale Element References**: Re-locates elements for each project
- **Modal Loading Issues**: Multiple fallback strategies for content detection
- **Network Timeouts**: Configurable wait times and retries
- **Missing Data**: Graceful handling with "N/A" values

## ⚠️ Important Notes

- **Rate Limiting**: The scraper includes delays to be respectful to the server
- **Headless Mode**: Runs without opening browser windows by default
- **Chrome Required**: Uses Chrome WebDriver (automatically managed)
- **Internet Connection**: Requires stable internet connection

## 🔍 Troubleshooting

### Common Issues

1. **"No projects were scraped"**
   - Check internet connection
   - Verify the RERA website is accessible
   - Try increasing wait times

2. **Chrome driver issues**
   - Ensure Chrome browser is installed
   - The script automatically downloads the correct ChromeDriver

3. **Modal not opening**
   - Website structure may have changed
   - Try running without headless mode to debug

### Debug Mode

To run in debug mode (visible browser):
```python
# Comment out this line in setup_selenium_driver()
# options.add_argument('--headless')
```

## 📝 Requirements

```txt
requests==2.31.0
beautifulsoup4==4.12.2
selenium==4.15.0
webdriver-manager==4.0.1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Disclaimer

This scraper is for educational and research purposes only. Please ensure you comply with:
- The website's robots.txt file
- Terms of service of the RERA Odisha portal
- Applicable data protection laws
- Rate limiting and respectful scraping practices

## 🙋‍♂️ Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Open an issue on GitHub
3. Provide detailed error messages and system information

## 🔄 Updates

- **v1.0.0** - Initial release with basic scraping functionality
- **v1.1.0** - Enhanced project name extraction
- **v1.2.0** - Improved modal handling and error recovery

---

**Made with ❤️ for RERA data extraction**

---
Answer from Perplexity: pplx.ai/share
