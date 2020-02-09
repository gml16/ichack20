import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
import ssl as ssl_lib
import certifi
import requests
from onboarding import Onboarding

from msg_handlers.message import Message
from msg_handlers.messagefilter import MessageFilter
from msg_handlers.chat_controller import ChatController
from msg_handlers.keyboard_control import KeyboardController
from collections import deque
from flask_socketio import SocketIO, emit

import time

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_TOKEN'])

socketio = SocketIO(app)

# For simplicity we'll store our app data in-memory with the following data structure.
# bot_sent = {"channel": {"user_id": onboarding}}
bot_sent = {}
state = {'setup': False}
#global triggered_key
waiting_keys = deque()
listening = True

@app.route('/')
def index():
    return "Hello world!"

@app.route('/test/')
def test_listener():
    return "<script> alert('ait'); var robot = require('robotjs'); " + \
            "     for (var x = 0; x < width; x++) " + \
            " { " + \
            "     y = 50 * Math.sin((4 * x) / 400) + 50; " + \
            "     robot.moveMouse(x, y); " + \
            " } " + \
           "robot.typeString('Hello World'); </script> "

@app.route('/listener/')
def listener():
    while listening:
        time.sleep(0.1)
        if len(waiting_keys):
            KeyboardController().press_keys(waiting_keys.popleft())

    return 200 #"Stopped listening"
    """
    return "<script src='//cdnjs.cloudflare.com/ajax/libs/socket.io/2.2.0/socket.io.js' integrity='sha256-yr4fRk/GU1ehYJPAs8P4JlTgu0Hdsp4ZKrx8bDEDC3I=' crossorigin='anonymous'></script>" + \
           "<script type='text/javascript' charset='utf-8'>"+ \
           "    var socket = io();" + \
           "    socket.on('connect', function() {" + \
           "        alert('hello');" + \
           "        socket.emit('my event', {data: 'connected!'});" + \
           "    });" + \
           "</script>"
    """

@socketio.on('connect')
def test_connect():
    emit('after connect',  {'data':'Lets dance'})
    print("connected")

@socketio.on('message')
def handle_message(message):
    print('received key: ' + message)

def start_onboarding(user_id: str, channel: str):
    # Create a new onboarding tutorial.
    onboarding_tutorial = Onboarding(channel)

    # Get the onboarding message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the onboarding message in Slack
    response = slack_web_client.chat_postMessage(**message)

    # Capture the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an onboarding task.
    onboarding_tutorial.timestamp = response["ts"]

    # Store the message sent in bot_sent
    if channel not in bot_sent:
        bot_sent[channel] = {}
    bot_sent[channel][user_id] = onboarding_tutorial


# ================ Team Join Event =============== #
# When the user first joins a team, the type of the event will be 'team_join'.
# Here we'll link the onboarding_message callback to the 'team_join' event.
@slack_events_adapter.on("team_join")
def onboarding_message(payload):
    """Create and send an onboarding welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    """
    event = payload.get("event", {})

    # Get the id of the Slack user associated with the incoming event
    user_id = event.get("user", {}).get("id")

    # Open a DM with the new user.
    response = slack_web_client.im_open(user_id)
    channel = response["channel"]["id"]

    # Post the onboarding message.
    start_onboarding(user_id, channel)


# ============= Reaction Added Events ============= #
# When a users adds an emoji reaction to the onboarding message,
# the type of the event will be 'reaction_added'.
# Here we'll link the update_emoji callback to the 'reaction_added' event.
@slack_events_adapter.on("reaction_added")
def update_emoji(payload):
    """Update the onboarding welcome message after receiving a "reaction_added"
    event from Slack. Update timestamp for welcome message as well.
    """
    event = payload.get("event", {})

    channel_id = event.get("item", {}).get("channel")
    user_id = event.get("user")

    if channel_id not in bot_sent:
        return

    # Get the original tutorial sent.
    onboarding_tutorial = bot_sent[channel_id][user_id]

    # Mark the reaction task as completed.
    onboarding_tutorial.reaction_task_completed = True

    # Get the new message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the updated message in Slack
    updated_message = slack_web_client.chat_update(**message)

    # Update the timestamp saved on the onboarding tutorial object
    onboarding_tutorial.timestamp = updated_message["ts"]


# =============== Pin Added Events ================ #
# When a users pins a message the type of the event will be 'pin_added'.
# Here we'll link the update_pin callback to the 'reaction_added' event.
@slack_events_adapter.on("pin_added")
def update_pin(payload):
    """Update the onboarding welcome message after receiving a "pin_added"
    event from Slack. Update timestamp for welcome message as well.
    """
    event = payload.get("event", {})

    channel_id = event.get("channel_id")
    user_id = event.get("user")

    # Get the original tutorial sent.
    onboarding_tutorial = bot_sent[channel_id][user_id]

    # Mark the pin task as completed.
    onboarding_tutorial.pin_task_completed = True

    # Get the new message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the updated message in Slack
    updated_message = slack_web_client.chat_update(**message)

    # Update the timestamp saved on the onboarding tutorial object
    onboarding_tutorial.timestamp = updated_message["ts"]


# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@slack_events_adapter.on("message")
def message(payload):
    """Display the onboarding welcome message after receiving a message
    that contains "start".
    """
    event = payload.get("event", {})

    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    print(f"Received {text}")

    if text and text.lower() == "start":
        return start_onboarding(user_id, channel_id)
    if text and text.lower() == "!clear":
        state['setup'] = False
    if text and state['setup']:
        return handle_new_message(user_id, channel_id, text)
    else:
        if text and text.lower().startswith('!setup'):
            return setup_controllers(user_id, channel_id, text)

def setup_controllers(user_id: str, channel: str, text: str):
    # Parses the message
    # Must be of the form:
    # !setup time/count value_of_update ip:port legal_moves_seperated_with_space
    tokens = text.split(' ')
    count = tokens[1].lower() == 'count'
    update_every = int(tokens[2]) if count else float(tokens[2])
    global ip, port
    ip, port = tokens[3].split(':')
    legal_moves = tokens[4:]

    print(f"Setup by {user_id} on #{channel}:\n{count}\n{update_every}\n{ip}:{port}\n{legal_moves}")

    # Initialise the command parsers
    global keyboard, chatController, chatFilter
    keyboard = KeyboardController()
    chatController = ChatController(keyboard, update_every=update_every, count=count)
    chatFilter = MessageFilter(legal_moves, chatController)

    state['setup'] = True

def handle_new_message(user_id: str, channel: str, text: str):
    # Takes the input and parses it
    message = Message(user_id+'#'+channel, text)
    valid, triggered_key = chatFilter.filter_message(message)
    print(f"{text} by {user_id} on #{channel} is {'' if valid else 'IN'}VALID")
    if triggered_key:
        print(f"Key '{triggered_key}' was hit")
        KeyboardController().press_keys(triggered_key)
        # waiting_keys.append(triggered_key)
        # requests.post(f'http://{ip}:{port}', json = {'key':triggered_key}, timeout=1)
        # curl --header "Content-Type: application/json" --request POST --data '{"key":KEYSTROKE}' IP:PORT

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    socketio.run(app)
