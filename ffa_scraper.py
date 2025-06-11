import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from typing import List, Optional
import subprocess
import traceback
import os
from tqdm import tqdm

class FFAScraper:
    """
    A class for scraping athlete data from the French Athletics Federation (FFA) website.

    This class provides methods to:
    - Search for athletes
    - Extract athlete information
    - Get athlete results
    - Handle rate limiting and errors
    """

    def __init__(self, base_url="https://bases.athle.fr/asp.net/athletes.aspx"):
        """
        Initialize the FFAScraper with the base URL.

        Args:
            base_url (str): The base URL for the FFA athlete search page
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Initialize Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Uncomment if you wish to run headless
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            # Get Chrome version
            chrome_version = subprocess.check_output(
                r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
                shell=True
            ).decode('UTF-8').strip().split()[-1]
            print(f"Chrome version: {chrome_version}")

            # Use ChromeDriverManager to download the driver
            driver_install_path = ChromeDriverManager().install()
            print(f"ChromeDriver install path: {driver_install_path}")

            # Extract the folder and build the correct executable path
            driver_folder = os.path.dirname(driver_install_path)
            chromedriver_path = os.path.join(driver_folder, "chromedriver.exe")
            print(f"Chromedriver executable path: {chromedriver_path}")

            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("WebDriver initialized successfully")
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            print("Please make sure you have Chrome browser installed and try again.")
            raise
    def __del__(self):
        # Clean up the WebDriver when the scraper is destroyed
        self.close()

    def close(self):
        """Explicitly close the WebDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("WebDriver closed successfully")

    def get_all_events(self, skip_events:List[str] = [], year: int = 2023):
        events = []
        seen_urls = set()
        page = 0

        while True:
            results_url = f"{self.base_url}/asp.net/liste.aspx?asp.net/liste.aspx?frmpostback=true&frmbase=resultats&frmmode=2&frmespace=0&frmsaison={year}&frmtype1=Hors+Stade&frmposition={page}"

            response = requests.get(results_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all competition rows
            rows = soup.find_all('tr')
            found_new_events = False

            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 18:
                    # Find the competition link cell (contains the event name)
                    competition_cell = None
                    for cell in cells:
                        if cell.get('class') and 'datasCMP0' in cell.get('class'):
                            link = cell.find('a')
                            if link:
                                competition_cell = cell
                                break

                    if competition_cell:
                        link = competition_cell.find('a')
                        competition_url = self.base_url + link['href']

                        # Skip if we've already seen this URL
                        if competition_url in seen_urls:
                            continue

                        found_new_events = True
                        seen_urls.add(competition_url)

                        competition_name = link.text.strip()
                        if competition_name in skip_events:
                            continue

                        # Extract date (4 cells before the competition cell)
                        date_cell = cells[cells.index(competition_cell) - 4]
                        date = date_cell.text.strip()

                        # Extract event type (2 cells before the competition cell)
                        event_type_cell = cells[cells.index(competition_cell) - 2]
                        event_type = event_type_cell.text.strip()

                        # Extract location (2 cells after the competition cell)
                        location_cell = cells[cells.index(competition_cell) + 2]
                        location = location_cell.text.strip()

                        events.append({
                            'date': date,
                            'name': competition_name,
                            'location': location,
                            'type': event_type,
                            'url': competition_url,
                            'competition_id': self._extract_competition_id(competition_url)
                        })
                        # print(f"Found event: {competition_name} on {date} in {location}")

            if not found_new_events:
                break

            time.sleep(1)
            page += 1

        return events

    def _extract_competition_id(self, url):
        match = re.search(r'frmcompetition=(\d+)', url)
        return match.group(1) if match else None

    def get_competition_athlets(self, url, skip_athlets:List[str]= []):

        print(f"\nGetting athlets form: {url}")
        results = []

        try:
            self.driver.get(url)

            # Wait for the page to load
            try:
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "datas1")))
            except:
                print("No results table found, checking for alternative content...")
                try:
                    self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                except:
                    print("Page failed to load completely")
                    return results

            # Check if we got an error page
            error_div = self.driver.find_elements(By.CSS_SELECTOR, 'div[style*="background-color:#990000"]')
            if error_div and 'Code Processing Error' in error_div[0].text:
                print("Error: Competition results not found or unavailable")
                return results

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')
                if not rows:
                    continue

                # Skip header rows containing 'Tri'
                if any('Tri' in cell.text for cell in rows[0].find_all('td')):
                    continue

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 5:
                        continue

                    rank = cells[0].text.strip()
                    time_text = cells[2].text.strip()
                    athlete_cell = cells[4]

                    athlete_link = athlete_cell.find('a')
                    if athlete_link:
                        athlete_name = athlete_link.text.strip()
                        if athlete_name in skip_athlets:
                            continue


                        # Locate and click the hyperlink using link text
                        try:
                            element = self.driver.find_element(By.LINK_TEXT, athlete_name)
                        except Exception as ex:
                            print(f"Error finding link for {athlete_name}: {ex}")
                            continue

                        original_window = self.driver.current_window_handle
                        element.click()

                        for window_handle in self.driver.window_handles:
                            if window_handle != original_window:
                                self.driver.switch_to.window(window_handle)
                                # soup = BeautifulSoup(self.driver.page_source, 'html.parser')


                                break
                        # Retrieve the content of the new page


                        # print(f"Retrieved content for athlete {athlete_name}")
                        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "innerDatas")))
                        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                        # print(soup)
                        athlete_page = self.driver.current_url

                        # Extract athlete_id from the onclick attribute if possible
                        # id_match = re.search(r"bddThrowAthlete\('resultats', (\d+),", onclick)
                        # athlete_id = id_match.group(1) if id_match else None

                        # if athlete_id:
                        results.append({
                                'rank': rank,
                                'time': time_text,
                                'athlete_name': athlete_name,
                                'athlete_page': athlete_page,

                            })

                        # Close the new window and switch back to the original window
                        self.driver.close()
                        self.driver.switch_to.window(original_window)
            return results

        except Exception as e:
            print(traceback.format_exc())
            print(f"Error getting competition results: {e}")
            print("Current URL:", self.driver.current_url)
            print("Page source:", self.driver.page_source[:500])  # Print first 500 chars of page source
            return results

    def save_results(self, results, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")

    def search_athletes(self, name, max_pages=10):
        """
        Search for athletes by name.

        Args:
            name (str): The name to search for
            max_pages (int): Maximum number of pages to search through

        Returns:
            list: List of dictionaries containing athlete information
        """
        athletes = []
        page = 1

        while page <= max_pages:
            url = f"{self.base_url}?nom={name}&p={page}"
            try:
                response = self.session.get(url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    athlete_rows = soup.find_all('tr', class_='ligne1') + soup.find_all('tr', class_='ligne2')

                    if not athlete_rows:
                        break

                    for row in athlete_rows:
                        cols = row.find_all('td')
                        if len(cols) >= 3:
                            athlete = {
                                'name': cols[0].text.strip(),
                                'club': cols[1].text.strip(),
                                'link': cols[0].find('a')['href'] if cols[0].find('a') else None
                            }
                            athletes.append(athlete)

                    page += 1
                    time.sleep(1)  # Rate limiting
                else:
                    print(f"Error: {response.status_code}")
                    break
            except Exception as e:
                print(f"Error searching athletes: {str(e)}")
                break

        return athletes

    def get_athlete_results(self, athlete_url, years=None):
        """
        Get results for a specific athlete.

        Args:
            athlete_url (str): The URL of the athlete's results page
            years (list): List of years to get results for. If None, gets all available years.

        Returns:
            dict: Dictionary containing athlete information and results
        """
        if years is None:
            years = range(2015, 2024)  # Default to last 9 years

        results = {
            'personal_info': {},
            'results': []
        }

        for year in years:
            url = f"{athlete_url}&saison={year}"
            try:
                response = self.session.get(url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Get personal info from first page only
                    if year == years[0]:
                        info_table = soup.find('table', class_='tableau1')
                        if info_table:
                            for row in info_table.find_all('tr'):
                                cols = row.find_all('td')
                                if len(cols) >= 2:
                                    key = cols[0].text.strip()
                                    value = cols[1].text.strip()
                                    results['personal_info'][key] = value

                    # Get results
                    results_table = soup.find('table', class_='tableau2')
                    if results_table:
                        for row in results_table.find_all('tr')[1:]:  # Skip header
                            cols = row.find_all('td')
                            if len(cols) >= 6:
                                result = {
                                    'date': cols[0].text.strip(),
                                    'competition': cols[1].text.strip(),
                                    'place': cols[2].text.strip(),
                                    'performance': cols[3].text.strip(),
                                    'wind': cols[4].text.strip(),
                                    'points': cols[5].text.strip()
                                }
                                results['results'].append(result)

                    time.sleep(1)  # Rate limiting
                else:
                    print(f"Error: {response.status_code}")
            except Exception as e:
                print(f"Error getting results: {str(e)}")

        return results

def main():
    """
    Main function to demonstrate the FFAScraper usage.
    """
    scraper = FFAScraper()

    # Example usage
    athletes = scraper.search_athletes("Dupont")
    if athletes:
        results = scraper.get_athlete_results(athletes[0]['link'])
        print(f"Found {len(athletes)} athletes")
        print(f"Got {len(results['results'])} results for {athletes[0]['name']}")

if __name__ == "__main__":
    main()
