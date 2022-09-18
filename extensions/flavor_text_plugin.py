import hikari
import hikari.api.rest
import lightbulb
import datetime
import utilities

plugin = lightbulb.Plugin('flavor_text_plugin')

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

@plugin.listener(lightbulb.events.CommandInvocationEvent)
async def command_listener(event):
    current_time = datetime.datetime.now().strftime("%m/%d/%y, %H:%M:%S")
    print(str(current_time) + f" [{event.context.get_guild().name}, #{str(event.context.get_channel())}] " + str(event.context.author) + f" used command '{event.command.name}'")

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

    text = f"{greeting_text} It is now `{str(current_time.hour).zfill(2)}:{str(current_time.minute).zfill(2)}`. {utilities.FLAVOR.get('wink')} (Aru is now online.)"
    await plugin.app.rest.create_message(channel = utilities.FLAVOR_TEXT_CHANNEL, content = text)

# When the bot is stopped, send a farewell
@plugin.listener(hikari.StoppingEvent)
async def start_bot(event):
    text = f"_Getting... sleepy..._ {utilities.FLAVOR.get('sleepy')} (Aru is now offline.)"
    await plugin.app.rest.create_message(channel = utilities.FLAVOR_TEXT_CHANNEL, content = text)

def load(bot):
    bot.add_plugin(plugin)