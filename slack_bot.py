from flask import Flask, request

from flask_slackbot import SlackBot
#from hidden_token import get_token
import os

app = Flask(__name__)
app.config['SLACK_TOKEN'] = os.environ.get('SLACK_TOKEN', None)
app.config['SLACK_CALLBACK'] = '/slack_callback'
app.debug = True
slackbot = SlackBot(app)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/slack_challenge', methods = ['POST'])
def slack_challenge():
    if request.method == 'POST':

        data = {
            "challenge"  : ''
        }
        js = json.dumps(data)

        resp = Response(js, status=200, mimetype='application/json')
        resp.headers['Link'] = request.url

        return resp



'''
The parameter of the callback function is a dict returns from the slack's outgoing api.
Here is the detail:
kwargs
{
    'token': token,
    'team_id': team_id,
    'team_domain': team_domain,
    'channel_id': channel_id,
    'channel_name': channel_name,
    'timestamp': timestamp,
    'user_id': user_id,
    'user_name': user_name,
    'text': text,
    'trigger_word': trigger_word
}'''
def fn1(kwargs):
    '''
    This function shows response the slack post directly without an extra post.
    In this case, you need to return a dict.'''
    return {'text': '!' + kwargs['text']} # Note the '!' character here is an user defined flag to tell the slack, this message is sent from the bot.


def fn2(kwargs):
    '''
    This function shows response the slack post indirectly with an extra post.
    In this case, you need to return None.
    Now the slack will ignore the response from this request, and if you need do some complex task you can use the built-in slacker.
    For more information, see https://github.com/os/slacker'''
    slackbot.slack.chat.post_message('#general', 'hello from slacker handler')
    return None


def fn3(text):
    '''
    This function is a filter, which makes our bot ignore the text sent from itself.'''
    return text.startswith('!')

slackbot.set_handler(fn1)
slackbot.filter_outgoing(fn3)


if __name__ == "__main__":
    app.run()
