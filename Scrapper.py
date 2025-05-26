import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
import re


def setup_selenium_driver():
    """Setup Selenium WebDriver with proper options"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def scrape_rera_projects():
    """Main function to scrape first 6 RERA projects"""
    driver = setup_selenium_driver()
    main_url = 'https://rera.odisha.gov.in/projects/project-list'

    try:
        projects_data = []

        # Process first 6 projects
        for i in range(6):
            print(f"\n{'=' * 50}")
            print(f"PROCESSING PROJECT {i + 1}/6")
            print(f"{'=' * 50}")

            try:
                # Navigate to main page for each project
                print(f"Loading main page for project {i + 1}...")
                driver.get(main_url)
                time.sleep(8)  # Wait for page to load completely

                # Find all "View Details" buttons on the current page
                view_details_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
                print(f"Found {len(view_details_buttons)} View Details buttons on page")

                if i >= len(view_details_buttons):
                    print(f"No more projects available. Found only {len(view_details_buttons)} projects.")
                    break

                # Get the specific button for this iteration (i-th button)
                button = view_details_buttons[i]

                # Scroll to the button to ensure it's visible
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(2)

                # Click the View Details button
                print(f"Clicking View Details button {i + 1}...")
                driver.execute_script("arguments[0].click();", button)
                time.sleep(5)  # Wait for modal to load

                # Extract project details from the modal
                project_info = extract_detailed_project_info(driver, i + 1)

                # Add project number for reference
                project_info['Project Number'] = f"Project {i + 1}"
                projects_data.append(project_info)

                print(f"Successfully extracted data for project {i + 1}")

                # Close the modal and return to main page
                close_modal(driver)
                time.sleep(3)

                # Ensure we're back on the main page
                print(f"Returning to main page after project {i + 1}")

            except Exception as e:
                print(f"Error processing project {i + 1}: {e}")
                # Try to close any open modal and return to main page
                close_modal(driver)
                time.sleep(2)
                continue

        return projects_data

    finally:
        driver.quit()


def extract_detailed_project_info(driver, project_num):
    """Extract detailed project information from the modal"""
    try:
        # Wait for modal content to load
        wait = WebDriverWait(driver, 15)

        project_info = {
            'Rera Regd. No': 'N/A',
            'Project Name': 'N/A',
            'Promoter Name': 'N/A',
            'Address of the Promoter': 'N/A',
            'GST No': 'N/A'
        }

        # Wait for modal to be visible
        try:
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-content, .modal-body, .project-details")))
            print(f"Modal loaded for project {project_num}")
        except TimeoutException:
            print("Modal might not have loaded properly, proceeding with current page content")

        # Get page source and parse immediately after modal opens
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract Project Name FIRST - as it appears immediately when modal opens
        project_name = extract_project_name_from_modal(soup, driver)
        if project_name:
            project_info['Project Name'] = project_name
            print(f"Found Project Name: {project_name}")

        # Extract RERA Registration Number
        rera_number = extract_rera_number(soup)
        if rera_number:
            project_info['Rera Regd. No'] = rera_number
            print(f"Found RERA No: {rera_number}")

        # Click on Promoter Details tab if available
        promoter_clicked = click_promoter_tab(driver)

        # Re-get page source after clicking promoter tab
        if promoter_clicked:
            soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract Promoter Details
        promoter_details = extract_promoter_details(soup)

        if promoter_details['company_name']:
            project_info['Promoter Name'] = promoter_details['company_name']
            print(f"Found Promoter: {promoter_details['company_name']}")

        if promoter_details['address']:
            project_info['Address of the Promoter'] = promoter_details['address']
            print(f"Found Address: {promoter_details['address'][:50]}...")

        if promoter_details['gst_no']:
            project_info['GST No'] = promoter_details['gst_no']
            print(f"Found GST: {promoter_details['gst_no']}")

        return project_info

    except Exception as e:
        print(f"Error extracting project details for project {project_num}: {e}")
        return {
            'Rera Regd. No': 'Error',
            'Project Name': 'Error',
            'Promoter Name': 'Error',
            'Address of the Promoter': 'Error',
            'GST No': 'Error'
        }


def extract_project_name_from_modal(soup, driver):
    """Extract project name from the modal - enhanced version"""
    try:
        # First try to get project name from modal title or header
        modal_selectors = [
            '.modal-title',
            '.modal-header h1',
            '.modal-header h2',
            '.modal-header h3',
            '.modal-header h4',
            '.modal-content h1',
            '.modal-content h2',
            '.modal-content h3',
            '.modal-body h1',
            '.modal-body h2',
            '.modal-body h3'
        ]

        for selector in modal_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if (text and len(text) > 3 and
                        'modal' not in text.lower() and
                        'close' not in text.lower() and
                        'orera' not in text.lower() and
                        'logo' not in text.lower()):
                    print(f"Found project name using selector {selector}: {text}")
                    return text

        # Try to find project name using Selenium directly from visible elements
        try:
            # Look for the first prominent heading in the modal
            heading_elements = driver.find_elements(By.CSS_SELECTOR,
                                                    ".modal-content h1, .modal-content h2, .modal-content h3, .modal-title")
            for element in heading_elements:
                if element.is_displayed():
                    text = element.text.strip()
                    if (text and len(text) > 3 and
                            'modal' not in text.lower() and
                            'close' not in text.lower() and
                            'orera' not in text.lower()):
                        print(f"Found project name using Selenium: {text}")
                        return text
        except:
            pass

        # Look for project name in table rows
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)

                    if 'project name' in label and value:
                        print(f"Found project name in table: {value}")
                        return value

        # Try regex patterns for project names
        page_text = soup.get_text()
        project_patterns = [
            r'Project Name\s*:?\s*([^\n\r]+)',
            r'Project\s*:?\s*([A-Z][^\n\r]+)',
            r'Name\s*:?\s*([A-Z][^\n\r]+(?:Project|Tower|Complex|Residency|Apartment)[^\n\r]*)'
        ]

        for pattern in project_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                project_name = match.group(1).strip()
                if len(project_name) > 3:
                    print(f"Found project name using regex: {project_name}")
                    return project_name

        # Last resort - look for any prominent text that might be project name
        all_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
        for heading in all_headings:
            text = heading.get_text(strip=True)
            if (text and len(text) > 5 and len(text) < 100 and
                    any(keyword in text.lower() for keyword in
                        ['project', 'tower', 'complex', 'residency', 'apartment', 'villa', 'homes']) and
                    'orera' not in text.lower() and
                    'modal' not in text.lower()):
                print(f"Found potential project name: {text}")
                return text

        return None

    except Exception as e:
        print(f"Error extracting project name: {e}")
        return None


def extract_rera_number(soup):
    """Extract RERA registration number"""
    try:
        # Multiple patterns to find RERA number
        rera_patterns = [
            r'(RP/\d+/\d+/\d+)',
            r'RERA\s*Regd\.?\s*No\.?\s*:?\s*([A-Z0-9/]+)',
            r'Registration\s*No\.?\s*:?\s*([A-Z0-9/]+)',
            r'RERA\s*No\.?\s*:?\s*([A-Z0-9/]+)',
            r'Reg\.?\s*No\.?\s*:?\s*([A-Z0-9/]+)'
        ]

        page_text = soup.get_text()

        for pattern in rera_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                # Clean up the RERA number
                rera_no = match.group(1).strip()
                # Remove any trailing text like "Registration"
                rera_no = re.sub(r'Registration.*$', '', rera_no).strip()
                return rera_no

        return None
    except:
        return None


def click_promoter_tab(driver):
    """Click on Promoter Details tab"""
    try:
        # Look for promoter tab with various selectors
        tab_selectors = [
            "//a[contains(text(), 'Promoter')]",
            "//a[contains(text(), 'Developer')]",
            "//a[contains(@href, 'promoter')]",
            "//li[contains(text(), 'Promoter')]//a",
            "//button[contains(text(), 'Promoter')]",
            "//tab[contains(text(), 'Promoter')]"
        ]

        for selector in tab_selectors:
            try:
                promoter_tab = driver.find_element(By.XPATH, selector)
                driver.execute_script("arguments[0].click();", promoter_tab)
                print("Successfully clicked Promoter Details tab")
                time.sleep(3)
                return True
            except:
                continue

        print("No Promoter Details tab found")
        return False

    except Exception as e:
        print(f"Error clicking promoter tab: {e}")
        return False


def extract_promoter_details(soup):
    """Extract promoter details from tables or structured content"""
    try:
        details = {
            'company_name': None,
            'address': None,
            'gst_no': None
        }

        # Extract from tables
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)

                    # Company Name
                    if any(keyword in label for keyword in
                           ['company name', 'promoter name', 'developer name', 'firm name']):
                        if value and value not in ['N/A', '-', '']:
                            details['company_name'] = value

                    # Address - look for registered office address specifically
                    elif 'registered office address' in label:
                        if value and value not in ['N/A', '-', '']:
                            # Clean up the address - remove extra commas and spaces
                            cleaned_address = re.sub(r',+', ', ', value)
                            cleaned_address = re.sub(r'\s+', ' ', cleaned_address).strip()
                            details['address'] = cleaned_address

                    # GST Number
                    elif any(keyword in label for keyword in ['gst no', 'gstin', 'gst number']):
                        if value and value not in ['N/A', '-', '']:
                            # Extract just the GST number, remove any trailing text
                            gst_match = re.search(r'([A-Z0-9]{15})', value)
                            if gst_match:
                                details['gst_no'] = gst_match.group(1)
                            else:
                                details['gst_no'] = value

        # If not found in tables, try regex patterns
        page_text = soup.get_text()

        if not details['company_name']:
            company_patterns = [
                r'Company Name\s*:?\s*([^\n\r]+)',
                r'Promoter Name\s*:?\s*([^\n\r]+)',
                r'by\s+([A-Z\s&.]+(?:PVT|LTD|LIMITED|PRIVATE|BUILDERS|DEVELOPERS|INFRA)[A-Z\s.]*)'
            ]
            for pattern in company_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['company_name'] = match.group(1).strip()
                    break

        if not details['address']:
            address_patterns = [
                r'Registered Office Address\s*:?\s*([^\n\r]+(?:\n[^\n\r]+)*?)(?=\n\s*[A-Z][a-z]+\s*:|GST|Entity|Email)',
            ]
            for pattern in address_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    address = match.group(1).strip()
                    # Clean up the address
                    address = re.sub(r',+', ', ', address)
                    address = re.sub(r'\s+', ' ', address).strip()
                    details['address'] = address
                    break

        if not details['gst_no']:
            gst_patterns = [
                r'GST\s*No\.?\s*:?\s*([A-Z0-9]{15})',
                r'GSTIN\s*:?\s*([A-Z0-9]{15})',
            ]
            for pattern in gst_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['gst_no'] = match.group(1).strip()
                    break

        return details

    except Exception as e:
        print(f"Error extracting promoter details: {e}")
        return {'company_name': None, 'address': None, 'gst_no': None}


def close_modal(driver):
    """Close any open modal"""
    try:
        # Try multiple methods to close modal
        close_methods = [
            "//button[contains(@class, 'close')]",
            "//button[contains(text(), 'Close')]",
            "//button[contains(text(), '×')]",
            "//a[contains(@class, 'close')]",
            "//*[@data-dismiss='modal']",
            "//button[@class='btn-close']"
        ]

        for method in close_methods:
            try:
                close_btn = driver.find_element(By.XPATH, method)
                driver.execute_script("arguments[0].click();", close_btn)
                print("Modal closed successfully")
                time.sleep(2)
                return True
            except:
                continue

        # If no close button found, try pressing ESC
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            print("Pressed ESC to close modal")
            time.sleep(2)
            return True
        except:
            pass

        # Try clicking outside the modal
        try:
            driver.execute_script("document.querySelector('.modal-backdrop').click();")
            print("Clicked modal backdrop to close")
            time.sleep(2)
            return True
        except:
            pass

        return False

    except Exception as e:
        print(f"Could not close modal: {e}")
        return False


def main():
    print("=== RERA ODISHA PROJECT SCRAPER ===")
    print("Scraping FIRST 6 projects exactly as requested...")
    print("Each project will be scraped individually by returning to main page")

    try:
        projects = scrape_rera_projects()

        if projects:
            print(f"\n{'=' * 80}")
            print("FINAL SCRAPED DATA - FIRST 6 PROJECTS")
            print(f"{'=' * 80}")

            for i, project in enumerate(projects, 1):
                print(f"\n{'-' * 60}")
                print(f"PROJECT {i}")
                print(f"{'-' * 60}")
                for key, value in project.items():
                    if key != 'Project Number':  # Don't print the project number field
                        print(f"{key}: {value}")

            print(f"\n{'=' * 80}")
            print(f"TOTAL PROJECTS SUCCESSFULLY SCRAPED: {len(projects)}")
            print(f"{'=' * 80}")
        else:
            print("❌ No projects were scraped. Please check the website structure.")

    except Exception as e:
        print(f"❌ Main execution error: {e}")


if __name__ == "__main__":
    main()
