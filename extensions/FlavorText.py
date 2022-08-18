import hikari
import hikari.api.rest
import lightbulb
import datetime

plugin = lightbulb.Plugin('FlavorText')
silentMode = False # if True, plugin will not load.

# Event functions
# When a message is sent in a guild, print the content associated with it (in the console).
@plugin.listener(hikari.GuildMessageCreateEvent) # Declarator for our function
async def print_message(event):
    if event.content == "ily aru":
        await plugin.app.rest.create_message(channel = 1009180448003465316, content = "ily2 :3c")
    
    print(event.content)

# When the bot is started
@plugin.listener(hikari.StartedEvent)
async def start_bot(event):
    now = datetime.datetime.now()
    currTime = str(now.time())[0:5]
    addText = ""
    if int(currTime[0:2]) >= 13:
        addText = " Oh, I guess it's the afternoon now. Good afternoon!!"
    elif int(currTime[0:2]) == 12:
        addText = " Oh, it's noon!"
    elif int(currTime[0:2]) < 6:
        addText = " It's late... Should you be up? I hope you can get some sleep soon."

    await plugin.app.rest.create_message(channel = 1009180448003465316, content = f"Good Morning! It is now {currTime}!{addText}")

# When the bot is stopped
@plugin.listener(hikari.StoppingEvent)
async def start_bot(event):
    await plugin.app.rest.create_message(channel = 1009180448003465316, content = f"_Getting... sleepy..._ (Aru is now offline.)")

def load(bot):
    if not silentMode:
        bot.add_plugin(plugin)