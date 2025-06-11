import requests
from bs4 import BeautifulSoup

# URL of the marathon results page on the French Athletics Federation site
results_url = "https://bases.athle.fr/asp.net/athletes.aspx?base=selections&seq=YOUR_SEQUENCE"


# Fetch the results page
response = requests.get(results_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the table with the results (you may need to adjust the selector)
results_table = soup.find('table', attrs={'class': 'results-table'})

# Loop over each row to extract basic runner details
runners = []
for row in results_table.find_all('tr')[1:]:  # skip header
    cols = row.find_all('td')
    if len(cols) > 1:
        name = cols[1].get_text(strip=True)
        time = cols[3].get_text(strip=True)
        profile_link = cols[1].find('a')['href'] if cols[1].find('a') else None
        runners.append({
            'name': name,
            'time': time,
            'profile_link': profile_link
        })

# For each runner, scrape the profile page for additional performances
for runner in runners:
    if runner['profile_link']:
        profile_url = "https://bases.athle.fr" + runner['profile_link']
        profile_response = requests.get(profile_url)
        profile_soup = BeautifulSoup(profile_response.content, 'html.parser')

        # Extract additional performance data (modify the selector as needed)
        performance_section = profile_soup.find('div', attrs={'id': 'performances'})
        performances = {}
        if performance_section:
            for event in performance_section.find_all('li'):
                event_name = event.find('span', class_='event-name').get_text(strip=True)
                event_time = event.find('span', class_='event-time').get_text(strip=True)
                performances[event_name] = event_time

        runner['performances'] = performances

# Now 'runners' is a list of dictionaries with all the data you need.
print(runners)
