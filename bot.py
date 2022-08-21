# Start a venv before working!
# python -m env env
# .\env\Scripts\activate

import hikari # Discord API Wrapper
import lightbulb # Command Handler for Hikari

bot = lightbulb.BotApp(
    token='MTAwOTE4MDIxMDgyMzk3MDk1Ng.GpqY3N.XZWBGDxihgVxDD3fLVfDPKmHRhRR6zv0NTMtLs', 
    default_enabled_guilds=(1004231179169443900),
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.GUILD_PRESENCES
) # Instantiate our bot

# bot.load_extensions('extensions.EventHandlers')
bot.load_extensions_from('./extensions')
bot.run() # Run the bot!