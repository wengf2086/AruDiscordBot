import hikari
import hikari.api.rest
import lightbulb
import datetime

plugin = lightbulb.Plugin('flavor_text_plugin')
silentMode = False # if True, plugin will not load.
flavorTextChannel = 1009180448003465316

# Event functions
# When a message is sent in a guild, print the content associated with it (in the console).
@plugin.listener(hikari.GuildMessageCreateEvent) # Declarator for our function
async def print_message(event):
    if str(event.content).lower() == "ily aru":
        await plugin.app.rest.create_message(channel = event.channel_id, content = "ily2 :3c", reply = event.message)
    elif str(event.content).lower() == "poyo":
        await plugin.app.rest.create_message(channel = event.channel_id, content = "Poyo poyo!", attachment = 'https://i.pinimg.com/564x/1e/0e/18/1e0e18550040066dcea3a4b2801e342f.jpg', reply = event.message)

    print(str(event.message.created_at.strftime("%m/%d/%y, %H:%M:%S")) + f" [{event.get_guild().name}, #{str(event.get_channel())}] " + str(event.author) + ": ", end ="")
    if event.content:
        print(event.content)
    
    if len(event.message.attachments) != 0:
        print("attachment(s): ", end = "")
        for attachment in event.message.attachments:
            print(attachment.url + ", ")
    
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
        addText = "It's late... Should you be up? I hope you can get some sleep soon."

    await plugin.app.rest.create_message(channel = flavorTextChannel, content = f"Good Morning! It is now {currTime}! {addText} <a:kirbywink:1011481550577213450>", user_mentions = True)

# When the bot is stopped
@plugin.listener(hikari.StoppingEvent)
async def start_bot(event):
    await plugin.app.rest.create_message(channel = flavorTextChannel, content = f"_Getting... sleepy..._ <:kirbysleeby:1009554855293096048> (Aru is now offline.)")

def load(bot):
    if not silentMode:
        bot.add_plugin(plugin)