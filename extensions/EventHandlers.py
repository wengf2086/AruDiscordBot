import hikari
import lightbulb

plugin = lightbulb.Plugin('EventHandlers')

# Event functions
# When a message is sent in a guild, print the content associated with it (in the console).
@plugin.listener(hikari.GuildMessageCreateEvent) # Declarator for our function
async def print_message(event):
    print(event.content)

# When the bot is started
@plugin.listener(hikari.StartedEvent)
async def start_bot(event):
    print('Aru is now online!')

@plugin.listener(hikari.GuildMessageCreateEvent) # Declarator for our function
async def print_message(event):
    if event.content == "Annie":
        await event.message.respond("is a poop!")

@plugin.listener(hikari.GuildMessageCreateEvent) # Declarator for our function
async def print_message(event):
    if event.content == "Jibba":
        await event.message.respond("is now 21!")

@plugin.listener(hikari.GuildMessageCreateEvent) # Declarator for our function
async def print_message(event):
    if event.content == "Omnom":
        await event.message.respond("just finished Chihayafuru!")

def load(bot):
    bot.add_plugin(plugin)