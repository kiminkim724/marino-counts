from collections import defaultdict
import json
from time import time
from flask import Flask, request, jsonify
from threading import Thread
from datetime import datetime
import pymongo
import os
from dotenv import load_dotenv


app = Flask(__name__)

names = {
	"1": "Marino Center - 2nd Floor", 
	"2": "Marino Center - 3rd Floor Select & Cardio", 
	"3": "Marino Center - 3rd Floor Weight Room",
	"4": "Marino Center - Gymnasium", 
	"5": "Marino Center - Track", 
	"6": "SquashBusters - 4th Floor"
}

def dayNameFromWeekday(weekday):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[weekday]

@app.route('/')
def home():
	return "Hello. the bot is alive!"

@app.route('/updateDB', methods=['POST'])
def updateDB():
	req = json.loads(request.data)
	for location, info in req.items():
		col = db[location]
		day = datetime.strptime(info[0], "%m/%d/%Y %I:%M %p").strftime('%A')
		hour = datetime.strptime(info[0], "%m/%d/%Y %I:%M %p").strftime('%H')
		try:
			x = col.insert_one({"Date": info[0], "Day": day, "Hour": hour, "Count": info[1]})
		except pymongo.errors.DuplicateKeyError:
			continue
	return {"status": "200"}

@app.route('/get/<id>', methods=['GET'])
def get(id):
	col = db[names[id]]
	counts = defaultdict(list)
	for count in col.find():
		day = count["Day"]
		hour = count["Hour"]
		counts[day].append([hour, count["Count"]])
	return jsonify(counts)

@app.route('/getAverage/<location_id>/<day_id>', methods=['GET'])
def getAverage(location_id, day_id):
	time_counts = {}
	name = names[location_id]
	col = db[name]
	day = dayNameFromWeekday(int(day_id))
	for hr in range(24):
		pipeline = [
			{
				"$match": { 
					"Day": day, 
					"Hour": str(hr) 
				}
			}, 
			{ 
				"$group": {
					"_id": "null",
					"TotalCount": {
						"$sum":1
					},
					"TotalAmount": {
						"$sum": "$Count"
					}
				}
			},
		]
		res = list(col.aggregate(pipeline))
		if res:
			time_counts[hr] = res[0]["TotalAmount"]/res[0]["TotalCount"]
	return jsonify(time_counts)

def initDB():
	global client, db
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

if __name__ == '__main__':
	initDB()
	app.run()