# Start a venv before working!
# python -m env env
# .\env\Scripts\activate
import random

import auxiliary

import hikari # Discord API Wrapper
import lightbulb # Command Handler for Hikari
import lavaplayer # Nodes manager for playing music

servers = 1004231179169443900, 133384813489946624, 700518641413652580

if __name__ == "__main__":
    bot = lightbulb.BotApp(
    token=auxiliary.TOKEN, 
    default_enabled_guilds=(servers), # , 752188244392935487
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.GUILD_PRESENCES,
    prefix = auxiliary.PREFIX,
    ) # Instantiate our bot

    random_activity_type = random.choice([0, 2, 3, 5])
    if random_activity_type == 0: # "Playing"
        activities = ["with your feelings ฅ(^ • ﻌ - ^)", "with your heart ฅ(^ • ﻌ - ^)"]
        
    elif random_activity_type == 2: # "Listening to"
        activities = ["the sound of your heart", "Bakamitai", "1, 2 Oatmeal", "NieR - Salvation", "Ado - 新時代", "BLACKPINK - Pink Venom"]

    elif random_activity_type == 3: # "Watching"
        activities = ["you... ฅ(^ • ﻌ - ^)", "Spirited Away", "Ping Pong the Animation", "To Your Eternity"]

    else: # "Competing in"
        activities = ["the battle for your love"]

    activity = random.choice(activities)
    bot.load_extensions_from('./extensions')
    bot.run(activity = hikari.Activity(name = activity, type = random_activity_type)) # Run the bot!