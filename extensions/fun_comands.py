import hikari
import lightbulb
import random

import utilities

plugin = lightbulb.Plugin('fun_commands')

@plugin.command 
@lightbulb.app_command_permissions()
@lightbulb.command('fun', 'Fun commands!')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def fun(ctx):
    pass

@fun.child
@lightbulb.option('server_id', 'Server to search for emojis. If unspecified, will search all emojis the bot is in.', required = False)
@lightbulb.option('message_id', 'ID of the message to be bombed. Will bomb the most recent message if not specified.', required = False)
@lightbulb.option('string', 'string to be contained in emojis', type = str, required = True)
@lightbulb.command('reactbomb', '\'Bombs\' a message with a bunch of random reactions containing a specified string.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def reactbomb(ctx):
    if ctx.options.message_id: # if a message is specified
        message = ctx.options.message_id
    else: # if no message specified, fetch last message
        channel = await plugin.app.rest.fetch_channel(channel = ctx.channel_id)
        message = channel.last_message_id

    # get all emojis that contain the specified string
    emojis = []
    servers = [int(ctx.options.server_id)] if ctx.options.server_id else utilities.SERVERS
    for server in servers:
        server_emojis = await plugin.app.rest.fetch_guild_emojis(guild = server)
        for emoji in server_emojis:
            if ctx.options.string in emoji.name:
                emojis.append(emoji)
    
    random.shuffle(emojis) # shuffle emojis
    num_reactions = len(emojis) if len(emojis) < 20 else 20

    for i in range(0, num_reactions):
        await plugin.app.rest.add_reaction(channel = ctx.channel_id, message = message, emoji = emojis[i])

@fun.child
@lightbulb.option('server_id', 'Server to search for emojis. If unspecified, will search all emojis the bot is in.', required = False)
@lightbulb.option('string', 'string to be contained in emojis', type = str, required = True)
@lightbulb.command('emojibomb', 'Sends bunch of random emojis containing a specified string.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def emojibomb(ctx):
    if ctx.options.message_id: # if a message is specified
        message = ctx.options.message_id
    else: # if no message specified, fetch last message
        channel = await plugin.app.rest.fetch_channel(channel = ctx.channel_id)
        message = channel.last_message_id

    # get all emojis that contain the specified string
    emojis = []
    servers = [int(ctx.options.server_id)] if ctx.options.server_id else utilities.SERVERS
    for server in servers:
        server_emojis = await plugin.app.rest.fetch_guild_emojis(guild = server)
        for emoji in server_emojis:
            if ctx.options.string in emoji.name:
                emojis.append(emoji)
    
    random.shuffle(emojis) # shuffle emojis
    num_reactions = len(emojis) if len(emojis) < 20 else 20

    content += f"{emojis[i].mention} "
    for i in range(0, num_reactions):
        content += f"{emojis[i].mention} "
    
    await plugin.app.rest.create_message(channel = ctx.channel_id, content = content)

@fun.child
@plugin.command
@lightbulb.option('question', 'What did you want to ask the Magic 8-Ball™?', type = str)
@lightbulb.command('8ball', 'Ask the Magic 8-Ball™ a yes/no question!')
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def eight_ball(ctx):

    pretext = "The Magic 8-Ball™ 🎱 says: "

    # 0 = negative, 1 = affirmative, 2 = non-committal
    responses = {
    "It is certain.": 1,
    "It is decidedly so.": 1,
    "Without a doubt.": 1,
    "Yes, definitely.": 1,
    "You may rely on it.": 1,
    "As I see it, yes.": 1,
    "Most likely.": 1,
    "Outlook good.": 1,
    "Yes.": 1,
    "Signs point to yes.": 1,
    "Reply hazy, try again.": 2,
    "Ask again later.": 2,
    "Better not tell you now.": 2,
    "Cannot predict now.": 2,
    "Concentrate and ask again.": 2,
    "Don't count on it.": 0,
    "My reply is no.": 0,
    "My sources say no.": 0,
    "Outlook not so good.": 0,
    "Very doubtful.": 0,
    }
    random_response = random.choice(list(responses.keys()))
    response = f"{pretext}_\"{random_response}\"_ "

    # 50% chance that the bot adds it's own input!
    if(random.randint(0,1) == 1):
        if responses.get(random_response) == 0: # if input is negative
            response += f"... But {utilities.BOT_NAME} thinks yes!" if random.randint(0,1) == 1 else f"But {utilities.BOT_NAME} doesn't think so..."
        elif responses.get(random_response) == 1: # if input is positive
            response += f"... But {utilities.BOT_NAME} thinks not!" if random.randint(0,1) == 1 else f"But {utilities.BOT_NAME} doesn't think so..."
        else: # if input is non-committal
            response += f"... But {utilities.BOT_NAME} thinks yes!" if random.randint(0,1) == 1 else f"... But {utilities.BOT_NAME} thinks not!"

    if isinstance(ctx, lightbulb.PrefixContext):
        await plugin.app.rest.create_message(content = response, channel = ctx.get_channel(), reply = ctx.event.message)
    else:
        await ctx.respond(f"{ctx.author.mention} asked: \"{ctx.options.question}\"" + f"\n{response}")

def load(bot):
    bot.add_plugin(plugin)