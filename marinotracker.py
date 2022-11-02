import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import re
import pymongo
import os
from dotenv import load_dotenv

names = {
	"1": "Marino Center - 2nd Floor", 
	"2": "Marino Center - 3rd Floor Select & Cardio", 
	"3": "Marino Center - 3rd Floor Weight Room",
	"4": "Marino Center - Gymnasium", 
	"5": "Marino Center - Track", 
	"6": "SquashBusters - 4th Floor"
}

load_dotenv()
conn_str =  os.getenv('MONGODB_URI')

# set a 5-second connection timeout
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
try:
	print(client.server_info())
except Exception:
	print("Unable to connect to the server.")
db = client["marinocount"]
for n, name in names.items():
	db[name].create_index("Date", unique = True)

if __name__ == "__main__":
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

        col = db[location]
        day = datetime.strptime(date, "%m/%d/%Y %I:%M %p").strftime('%A')
        hour = datetime.strptime(date, "%m/%d/%Y %I:%M %p").strftime('%H')
        try:
            x = col.insert_one({"Date": date, "Day": day, "Hour": hour, "Count": count})
        except pymongo.errors.DuplicateKeyError:
            continue
