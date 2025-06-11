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
    def __init__(self):
        self.base_url = "https://bases.athle.fr"
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

def main():
    scraper = FFAScraper()
    df = pd.read_csv(r"data/athlets.csv")
    athlets = df['athlet'].tolist()
    athlets_pages = df['athlet_page'].tolist()
    try:
        events = scraper.get_all_events(year=2021)
        print(f"Found {len(events)} events")
        for event in tqdm(events, total=len(events)):
            results = scraper.get_competition_athlets(event['url'],skip_athlets=athlets)
            # Optionally, print out details from results
            for result in results:
                print(f"Athlete: {result['athlete_name']}, page: {result['athlete_page']}")
                athlets.append(result['athlete_name'])
                athlets_pages.append(result['athlete_page'])
    except Exception as e:
        raise e


    finally:
        # Explicitly close the WebDriver when we're done
        scraper.close()

        df = pd.DataFrame({'athlet':athlets, 'athlet_page':athlets_pages})
        df = df.drop_duplicates()
        df.to_csv(r"data/athlets.csv", header=True, index=False)

if __name__ == "__main__":
    main()
