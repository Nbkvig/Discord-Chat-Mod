# flask_app.py
# this is the API for discord bot.

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Data structure for stats
bot_stats = {
    "guilds": [],
    "voice-channels": [],
    "text-channels": [],
    "roles": [],
    "users": 0,
    "status": "offline"

}


# Updates data structure
def update_bot_stats(guilds, user_count, status, voice_channels, text_channels, roles):
    bot_stats['guilds'] = guilds
    bot_stats['users'] = user_count
    bot_stats['status'] = status
    bot_stats['voice-channels'] = voice_channels
    bot_stats['text-channels'] = text_channels
    bot_stats['roles'] = roles


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
    app.run(host='0.0.0.0', port=8005, debug=False)
