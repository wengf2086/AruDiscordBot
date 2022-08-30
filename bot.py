# Start a venv before working!
# python -m env env
# .\env\Scripts\activate
import random

import utilities

import hikari # Discord API Wrapper
import lightbulb # Command Handler for Hikari

if __name__ == "__main__":
    bot = lightbulb.BotApp(
            token = utilities.TOKEN, 
            default_enabled_guilds = utilities.SERVERS,
            intents = hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.GUILD_PRESENCES,
            prefix = utilities.PREFIX
    ) # Instantiate our bot

    # Choose a random activity to display
    random_activity = utilities.get_random_activity() # Get a random activity to display

    bot.load_extensions_from('./extensions') # Load all extensions
    bot.run(activity = hikari.Activity(name = random_activity[0], type = random_activity[1])) # Run the bot!

    