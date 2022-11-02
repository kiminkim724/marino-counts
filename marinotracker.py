import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# keep_alive function, that maintains continuous
# running of the code.
from keep_alive import keep_alive
import pytz
import re

URL = "http://0.0.0.0:8080"
# to start the thread
if __name__ == "__main__":
    keep_alive()
    counts = {}
    while(True):
        tz_US = pytz.timezone('US/Eastern')
        datetime_US = datetime.now(tz_US)
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
        }

        # this is just to get the time at the time of web scraping
        current_day = datetime_US.weekday()
        current_hour = datetime_US.hour
        try:
            response = requests.get('https://connect2concepts.com/connect2/?type=circle&key=2A2BE0D8-DF10-4A48-BEDD-B3BC0CD628E7', headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        text = response.text
        html_data = BeautifulSoup(text, 'html.parser')
        sections = html_data.find_all("div", {"style": "text-align:center;"})
        
        for section in sections:
            text = list(section.stripped_strings)
            location = text[0]
            count = int(re.search('(?<=Last Count: ).*', text[2]).group(0))
            date = re.search('(?<=Updated: ).*', text[3]).group(0)
            counts[location] = (date, count)
        
        requests.post(URL+"/updateDB", json=counts)
        time.sleep(1800)
