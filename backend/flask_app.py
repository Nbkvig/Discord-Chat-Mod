# flask_app.py
#
# Starts the dashboard for people to see bot data.
# Also provides an API. 
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(
    __name__,
    static_folder='../frontend/dist'
)
CORS(app)


# =================================
# Flask API
# =================================


bot_stats = {
    "guilds": [],
    "voice-channels": [],
    "text-channels": [],
    "roles": [],
    "recent-actions": [],
    "users": 0,
    "status": "offline"

}


def update_bot_stats(guilds, user_count, status, voice_channels, text_channels, roles):
    bot_stats['guilds'] = guilds
    bot_stats['users'] = user_count
    bot_stats['status'] = status
    bot_stats['voice-channels'] = voice_channels
    bot_stats['text-channels'] = text_channels
    bot_stats['roles'] = roles

@app.route('/api/bot-stats')
def get_bot_stats():    
    return jsonify(bot_stats)


@app.route('/api/recent-actions')
def get_recent_actions():
    try:
        with open('data/logs.json', 'r') as f:
            actions = json.load(f)
        return jsonify(actions[-5:])
    except FileNotFoundError:
        return jsonify([])

# =================================
# React Dashboard
# =================================


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):

    if path == "":
        return send_from_directory(app.static_folder, 'index.html')
    

    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    
    
    return send_from_directory(app.static_folder, 'index.html')


def run_flask():
    app.run(host='0.0.0.0', port=8005, debug=False)
