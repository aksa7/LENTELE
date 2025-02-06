from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
import random
import datetime

app = Flask(__name__)

client = MongoClient("mongodb+srv://gndr:Isbandymas123@gndr123.sr19d.mongodb.net/")
db = client['DB']
collection = db["events"]

@app.route('/')
def index():
    months = {i: [] for i in range(1, 13)}
    events = collection.find().sort("date", 1)

    for event in events:
        event_month = event['date'].month
        months[event_month].append(event)

    month_names = {
        1: "Sausis", 2: "Vasaris", 3: "Kovas", 4: "Balandis",
        5: "Gegužė", 6: "Birželis", 7: "Liepa", 8: "Rugpjūtis",
        9: "Rugsėjis", 10: "Spalis", 11: "Lapkritis", 12: "Gruodis"
    }

    return render_template('index.html', months=months, month_names=month_names)

@app.route('/add', methods=['POST'])
def add_event():
    name = request.form['name']
    date_str = request.form['date']

    try:
        event_date = datetime.datetime.strptime(date_str, '%m/%d')
        event_date = event_date.replace(year=datetime.datetime.now().year)
        collection.insert_one({'name': name, 'date': event_date})
    except ValueError:
        pass

    return redirect('/')

@app.route('/delete_all', methods=['POST'])
def delete_all():
    collection.delete_many({})
    return redirect('/')

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    results = {}
    all_events = list(collection.find().sort("date", 1))

    if request.method == 'POST':
        input_date = request.form['date']

        try:
            date = datetime.datetime.strptime(input_date, '%m/%d')
            date = date.replace(year=datetime.datetime.now().year)
            past_events = list(collection.find({'date': {'$lte': date}}).sort("date", 1))
            results['past_events'] = past_events
            results['date_entered'] = date.strftime('%m/%d')
        except ValueError:
            results['error'] = "Netinkama datos forma! Naudokite formatą MM/DD."

    results['all_events'] = all_events
    return render_template('stats.html', results=results)

def initialize_events():
    if collection.count_documents({}) == 0:
        for i in range(50):
            random_month = random.randint(1, 12)
            random_day = random.randint(1, 28)
            event_date = datetime.datetime(datetime.datetime.now().year, random_month, random_day)
            collection.insert_one({
                'name': f'Testinis renginys {i + 1}',
                'date': event_date
            })

if __name__ == '__main__':
    initialize_events()
    app.run(debug=True)
