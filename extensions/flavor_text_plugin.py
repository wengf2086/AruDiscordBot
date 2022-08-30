import hikari
import hikari.api.rest
import lightbulb
import datetime

plugin = lightbulb.Plugin('flavor_text_plugin')
flavorTextChannel = 1014275372856123424

# When a message is sent, print it
@plugin.listener(hikari.GuildMessageCreateEvent)
async def message_listener(event):
    # Logger
    print(str(event.message.created_at.strftime("%m/%d/%y, %H:%M:%S")) + f" [{event.get_guild().name}, #{str(event.get_channel())}] " + str(event.author) + ": ", end ="")
    if event.content:
        print(event.content)
    
    if len(event.message.attachments) != 0:
        print("attachment(s): ", end = "")
        for attachment in event.message.attachments:
            print(attachment.url + ", ")

    if len(event.message.embeds) != 0:
        print("sent an embed")
    
# When the bot is started, send a greeting
@plugin.listener(hikari.StartedEvent)
async def start_bot(event):
    current_time = datetime.datetime.now()
    current_hour = current_time.hour

    if current_hour < 6: # Late Night / Early Morning
        greeting_text = "Oh... you're still up? It's late!"
    elif current_hour < 12: # Morning
        greeting_text = "Good morning!"
    elif current_hour == 12: # Noon
        greeting_text = "Oh, it's noon already?"
    else: # Afternoon
        greeting_text = "Good afternoon!"

    text = f"{greeting_text} It is now `{current_time.hour}:{current_time.minute}`. <a:kirbywink:1011481550577213450> (Aru is now online.)"
    await plugin.app.rest.create_message(channel = flavorTextChannel, content = text)

# When the bot is stopped, send a farewell
@plugin.listener(hikari.StoppingEvent)
async def start_bot(event):
    text = f"_Getting... sleepy..._ <:kirbysleeby:1009554855293096048> (Aru is now offline.)"
    await plugin.app.rest.create_message(channel = flavorTextChannel, content = text)

def load(bot):
    bot.add_plugin(plugin)