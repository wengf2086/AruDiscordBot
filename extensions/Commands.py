from asyncio.windows_events import NULL
import hikari
import lightbulb
import re

plugin = lightbulb.Plugin('Commands')
reactCarpetBombMode = False # if True, every message will have reactions added to it...!
carpetBombChannelId = 0
carpetBombEmojis = []

@plugin.listener(hikari.GuildMessageCreateEvent) # Declarator for our function
async def carpetBomb(event):
    if event.channel_id == carpetBombChannelId and reactCarpetBombMode:
        for emoji in carpetBombEmojis:
            await plugin.app.rest.add_reaction(channel = carpetBombChannelId, message = event.id, emoji = emoji)

# Command functions
@plugin.command
@lightbulb.option('emojis', 'emojis to be used as reactions. Only default emojis and emojis from this server are allowed.', type = str, required = False)
@lightbulb.option('channel', 'ID of the channel to be carpet bombed', required = False)
@lightbulb.command('togglereactcarpetbombmode', 'Toggle React Carpet Bomb Mode on/off. When turning on, must specify channel ID.')
@lightbulb.implements(lightbulb.SlashCommand)
async def togglereactcarpetbombmode(ctx):
    if ctx.options.channel:
        channel_str = re.split(r'<#|>', ctx.options.channel)
        carpetBombChannelId = channel_str[0] if (len(channel_str) == 1) else channel_str[1]
    if ctx.options.emojis:
        for emoji_str in ctx.options.emojis.split(" "):
            carpetBombEmojis.append(hikari.Emoji.parse(emoji_str))

    reactCarpetBombMode = True if not reactCarpetBombMode else False

@plugin.command
@lightbulb.option('emojis', 'emojis to be used as reactions. Only default emojis and emojis from this server are allowed.', type = str)
@lightbulb.option('message_id', 'ID of the message to be bombed')
@lightbulb.option('channel', 'ID of the channel of the message to be bombed')
@lightbulb.command('reactbomb', '\'Bombs\' a message with a bunch of (MAX: 20) reactions!')
@lightbulb.implements(lightbulb.SlashCommand)
async def reactbomb(ctx):
    channel_str = re.split(r'<#|>', ctx.options.channel)
    channel = channel_str[0] if (len(channel_str) == 1) else channel_str[1]

    for emoji_str in ctx.options.emojis.split(" "):
        emoji = hikari.Emoji.parse(emoji_str)
        await plugin.app.rest.add_reaction(channel = channel, message = ctx.options.message_id, emoji = emoji)

@plugin.command
@lightbulb.command('group', 'This is a group')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def my_group(ctx):
    pass

@my_group.child
@lightbulb.command('subcommand', 'This is a subcommand')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def subcommand(ctx):
    await ctx.respond('I am a subcommand!')

@plugin.command
@lightbulb.option('str2', 'The second number', type=int)
@lightbulb.option('str1', 'The first number', type=int)
@lightbulb.command('add', 'Add two numbers together')
@lightbulb.implements(lightbulb.SlashCommand)
async def add(ctx):
    await ctx.respond(ctx.options.num1 + ctx.options.num2)

def load(bot):
    bot.add_plugin(plugin)