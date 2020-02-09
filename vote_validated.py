

class ValidateVote:
    """Constructs the onboarding message and stores the state of which tasks were completed."""

    # TODO: Create a better message builder:
    # https://github.com/slackapi/python-slackclient/issues/392
    # https://github.com/slackapi/python-slackclient/pull/400
    def voted_block(self, vote):
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"Bip boop... chat has voted to do **{vote.upper()}**"
                ),
            },
        }

    def __init__(self, channel, vote):
        self.channel = channel
        self.vote = vote
        self.username = "VotingBot"
        self.icon_emoji = ":robot_face:"
        self.timestamp = ""

    def get_message_payload(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                self.voted_block(self.vote)
            ],
        }
