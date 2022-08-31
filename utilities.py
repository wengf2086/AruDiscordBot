import os.path
from os import listdir
import random
import requests
import datetime
import os.path

from sql_functions import Gif
# Constants
SERVERS = 1004231179169443900, 133384813489946624, 700518641413652580, 1014274983721193563
TOKEN = 'MTAwOTE4MDIxMDgyMzk3MDk1Ng.Gk5Ed7.7yyTgguB2cq00yH6P6ZQ7atrUEOa_TQwDvudBI'
PREFIX = "a!"
LOG_FILE_NAME = "log.txt"
BOT_NAME = "Aru"

# Dictionaries
ACTIONS = { # Contains actions and their respective texts
    'blush': "{actor} is blushing at you, {recipient}!", 
    'bonk': "{recipient}, you have been bonked by {actor}!", 
    'cuddle': "Aww! {recipient}, you are being cuddled by {actor}!", 
    'highfive': "{actor} high fived {recipient}!", 
    'holdhands': "{actor} is holding {recipient}'s hand!", 
    'hug': "{recipient}, you have been hugged by {actor}!", 
    'kick': "{recipient}, you have been kicked by {actor}!", 
    'kiss': "{recipient}, you have been kissed by {actor}!", 
    'laugh': "{actor} is laughing at you, {recipient}!", 
    'nom': "{recipient}, you have been nommed by {actor}!",
    'pat': "{recipient}, you have been patted by {actor}!", 
    'poke': "{recipient}, you have been poked by {actor}!", 
    'punch': "{recipient}, you have been punched by {actor}!", 
    'shoot': "{recipient}, you have been shot by {actor}!", 
    'slap': "{recipient}, you have been slapped by {actor}!", 
    'stare': "{recipient}, you are being stared at by {actor}.", 
    'tuckin': "{recipient}, you have been tucked in by {actor}. Sweet dreams!", 
    'wink': "{recipient}, {actor} is winking at you!", 
    'yeet': "{recipient} has been yeeted by {actor}!"
}

STATUS_EMOJIS = { # Contains emojis for each status
    "online": "<a:status_online:1014291128704585848>",
    "idle": "<a:status_idle:1014291127895068682>",
    "dnd": "<a:status_dnd:1014291126590648393>",
    "offline": "<:status_offline:1014291125462376460>",
    "mobile": "<:status_mobile:1014291800980197396>"
}

# Helper Functions
# Return a random activity and activity type
def get_random_activity():
    '''
    Returns a random activity and activity type.
    '''

    random_activity_type = random.choice([0, 2, 3, 5])
    if random_activity_type == 0: # "Playing"
        activities = ["with your feelings ฅ(^ • ﻌ - ^)", "with your heart ฅ(^ • ﻌ - ^)"]
        
    elif random_activity_type == 2: # "Listening to"
        activities = ["the sound of your heart", "Bakamitai", "1, 2 Oatmeal", "NieR - Salvation", "Ado - 新時代"]

    elif random_activity_type == 3: # "Watching"
        activities = ["you... ฅ(^ • ﻌ - ^)", "Spirited Away", "Ping Pong the Animation", "To Your Eternity"]

    else: # "Competing in"
        activities = ["the battle for your love"]

    return random.choice(activities), random_activity_type

# Return a list containing the names of all available action
def get_all_action_names():
    '''
    Returns a list containing strings of all the available actions
    '''
    onlyfiles = [f for f in listdir("C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/") if os.path.isfile(os.path.join("C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/", f))]
    action_names = []
    for file in onlyfiles:
        name = file.split("_")[1]
        action_names.append(name)

    return action_names

# Updates database with GIFs from nekos.best API.
def nekos_best_api_update():
    available_actions = ["baka", "bite", "blush", "bored", "cry", "cuddle", "dance", "facepalm", "feed", "handhold", "happy", "highfive", "hug", "kick", "kiss", "laugh", "pat", "poke", "pout", "punch", "shoot", "shrug", "slap", "sleep", "smile", "smug", "stare", "think", "thumbsup", "tickle", "wave", "wink", "yeet"]
    author_id = 173555466176036864
    # This bot has some different names for actions; this dictioanry serves as a translator.
    # Bot's name : nekos.best API's name
    nekos_best_api_action_names = {
        'holdhands': 'handhold'
    }

    for action in list(ACTIONS.keys()):
        if action not in available_actions:
            continue

        action_name = nekos_best_api_action_names.get(action, action) # if nekos.best API has a different name, use theirs.
        num_gifs = int(requests.get("https://nekos.best/api/v2/endpoints").json()[action_name]['max']) # Number of nekos.best API GIFs available for this action

        for i in range(0, num_gifs):
            # Fetch the GIF for this index by padding the index with zeroes to create a string of length 3, and using the following format
            gif_link = "https://nekos.best/api/v2/" + action_name + f"/{str(i).zfill(3)}" + ".gif"

            if not Gif.get_gif_from_link(gif_link): # If the link is not in the database, add it
                Gif.add_gif(action, author_id, gif_link)
                print(f"{action}: '{gif_link}' added")
            else:
                print(f"{action}: '{gif_link}' not added. Already in database")
    return