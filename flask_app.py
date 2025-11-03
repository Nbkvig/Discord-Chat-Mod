from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# TODO: Replace this with calls to get the real data. 
bot_stats = {
    "guilds": [],
    "users": 0,
    "status": "offline"
}

def update_bot_stats(guilds, user_count, status):
    bot_stats['guilds'] = guilds
    bot_stats['users'] = user_count
    bot_stats['status'] = status

@app.route('/api/bot-stats', methods=['GET'])
def get_bot_stats():    
    return jsonify(bot_stats)

@app.route('/')
def home():
        return render_template('home.html', guilds=get_guilds())

def get_guilds():
    file = open('guilds.txt', 'r')
    data = file.readlines()
    file.close()
    data = [i.replace('\n','') for i in data]
    data = [i.split(":") for i in data]
    guilds = data
    return guilds

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)