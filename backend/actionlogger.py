import json
from datetime import datetime

# ======================================
# JSON logs
# ======================================
# basic json action log helper function. 

def log_action(message):

    action = {
        "message": message,
        "time": datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }

    try:
        with open('data/logs.json', 'r') as f:
            actions = json.load(f)
    except:
        actions = []

    actions.append(action)

    if len(actions) > 5:
        actions = actions[-5:]

    with open('data/logs.json', 'w') as f:
        json.dump(actions, f)