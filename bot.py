# Start a venv before working!
# python -m env env
# .\env\Scripts\activate

import hikari # Discord API Wrapper
import lightbulb # Command Handler for Hikari

bot = lightbulb.BotApp(
    token='MTAwOTE4MDIxMDgyMzk3MDk1Ng.Gk5Ed7.7yyTgguB2cq00yH6P6ZQ7atrUEOa_TQwDvudBI', 
    default_enabled_guilds=(1004231179169443900), # , 752188244392935487, 133384813489946624
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.GUILD_PRESENCES
) # Instantiate our bot

bot.load_extensions_from('./extensions')
bot.run() # Run the bot!