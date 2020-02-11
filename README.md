# IC Hack 2020

## Inspiration

We were inspired to work on this project by the famous "Twitch Plays Pokemon" stream, where users in chat were able to vote for keystrokes being executed in game. 

## What it does

Our product works as an extended version. Streamers on **any** streaming service, playing **any** game, can now use our platform to define which keys are "controllable" by their viewers. After inviting them to their Slack channel, where our bot is present, viewers can interact and/or vote with their messages for the next keys to be sent in real-time. Watch the demo [here](https://www.youtube.com/watch?v=q__uzQtw48o). Our hack is on [DevPost](https://devpost.com/software/play4us).

## How we built it

The platform is built in Python Flask. It runs through Ngrok locally, or Heroku. The Slack API is used to send the message contents to our server. Messages are filtered and aggregated every x seconds or x messages (set by the streamer) before being sent to the streamers' OS. 
