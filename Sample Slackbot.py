import os
import time
import re
from slackclient import SlackClient

# Statics
SLACK_TOKEN = "xoxb-371305192545-371166466304-pAegcv00tZ1LOThb2iZxp2pV"
RTM_READ_DELAY = 1
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# Variables
slack_client = SlackClient(SLACK_TOKEN)
bot_id = None
command_response_map = dict()


def process_command(slack_events) :
    """
    process_comand processes events that have happened in a particular Slack Channel,
    and returns the user query presented to the bot and the channel of origin for
    further processing and determination of bot output.

    :param slack_events: A list of events that have been listened by the bot
    :return: Returns a tuple of the user query presented to the bot and the channel of origin
    """

    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = None, None
            bot_command = re.search(MENTION_REGEX, event["text"])
            if bot_command:
                user_id, message = (bot_command.group(1), bot_command.group(2).strip())

            if user_id == bot_id:
                return message, event["channel"]
    return None, None


def respond(command, channel) :
    """

    :param command: The user query presented to the bot
    :param channel: The command's channel of origin
    :return: Return's the bot's response to a user command
    """
    response = None

    try:
        response = command_response_map[command]
    except:
        if command == "commands":
            response = "Here are some commands you could use:\n"
            for string in command_response_map.keys():
                response += string +"\n"

    slack_client.api_call("chat.postMessage", channel=channel, text=response, username = 'GBot', icon_emoji=':grinning:')


def initialize_responses() :
    """
    Initializes responses for each user query / command, and stores it in a dictionary
    """
    command_response_map['hello'] = "Hey there! I am GBot"
    command_response_map['weather'] = "The weather might be good, but I'm not really sure..."


initialize_responses()

print("Server Started")
if slack_client.rtm_connect(with_team_state=False):
    bot_id = slack_client.api_call("auth.test")["user_id"]

    while True:
        command, channel = process_command(slack_client.rtm_read())
        if command:
            respond(command, channel)

        time.sleep(RTM_READ_DELAY)
else:
    print("Connection Failed")