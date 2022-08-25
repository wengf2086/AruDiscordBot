import hikari
import lightbulb
import random

plugin = lightbulb.Plugin('fun_commands')

presets = {
    'kirby': "<a:kirbeats:1009554827098988574> <a:kirbydance:1009554839602204712> <a:kirbydance2:1009554838692044900> <a:kirbyfortnitedance:1009554841963606146> <a:kirbyhi:1009554846967414874> <a:kirbybye:1009554837064650923> <a:kirbyyay:1009554865145528501> <a:kirbyok:1009554850914242754><a:kirbylink:1009554849131675808> <a:kirbyroll:1009554852046700644> <a:kirbyrun:1009554853091082240> <a:kirbyshock:1009554854215168050> <a:kirbyspin:1009554856194867205> <a:kirbyswim:1009554860489842750> <a:kirbyuwu:1009554861739749478> <a:kirbywave:1009554864285683824> <:kirbo:1009554829141606490> <:kirby:1009554833478537377> <:kirbybuffed:1009554836255166474>",
    'sparkles': "<a:sparkles2:1009553998447128586> <a:sparkles3:1009553999353090232> <a:sparkles4:1009554000393277513> <a:sparkles5:1009554001588662418> <a:sparkles6:1009554002515607584> <a:sparkles7:1009554003799068672> <a:sparkles8:1009554004973469807> <a:sparkles9:1009554005342560318> <a:sparkles10:1009554006462451802> <a:sparkles11:1009554007263547533> <a:sparkles12:1009554008261787658> <a:sparkles13:1009554009306189824> <a:sparkles14:1009554009985667172> <a:sparkles15:1009554010920992918> <a:sparkles16:1009554011764031608><a:pinkstars:855509222635733032><a:sparkles1:1009553997054619669><a:sparkles11:1009554007263547533> <a:sparkles16:1009554011764031608>"
}


@plugin.command 
@lightbulb.app_command_permissions()
@lightbulb.command('fun', 'Fun commands!')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def fun(ctx):
    pass

@fun.child
@lightbulb.command('temp', 'temp command')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def temp(ctx):
    for emoji in (await plugin.app.rest.fetch_guild_emojis(ctx.get_guild())):
        print(emoji)

@fun.child
@lightbulb.option('emojis', 'emojis / preset to be used as reactions. Only default emojis and emojis from this server allowed.', type = str, required = True)
@lightbulb.option('message_id', 'ID of the message to be bombed. Will bomb the most recent message if not specified.', required = False)
@lightbulb.command('reactbomb', '\'Bombs\' a message with a bunch of (MAX: 20) reactions!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def reactbomb(ctx):
    all_emojis = await ctx.get_guild().fetch_emojis()
    str = ""
    for emoji in all_emojis:
        str += f"{emoji} "
    print(str)
    if ctx.options.message_id: # message is specified
        message = ctx.options.message_id
    else: # no message specified, react to last message
        channel = await plugin.app.rest.fetch_channel(channel = ctx.channel_id)
        message = channel.last_message_id

    if  presets.get(ctx.options.emojis, "NONE") != "NONE":
        emojis = presets.get(ctx.options.emojis, "NONE")

    elif ctx.options.emojis:
        emojis = ctx.options.emojis
    
    else:
        ctx.respond("Error: Invalid preset or emoji. Only default emojis and emojis from this server allowed. Please try again!")

    for emoji_str in emojis.split(" "):
        emoji = hikari.Emoji.parse(emoji_str)
        await plugin.app.rest.add_reaction(channel = ctx.channel_id, message = message, emoji = emoji)

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

    # 50% chance that Aru adds her own input!
    if(random.randint(0,1) == 1):
        if responses.get(random_response) == 0: # if input is negative
            response += "... But Aru thinks yes!" if random.randint(0,1) == 1 else "But Aru doesn't think so..."
        elif responses.get(random_response) == 1: # if input is positive
            response += "... But Aru thinks not!" if random.randint(0,1) == 1 else "But Aru doesn't think so..."
        else: # if input is non-committal
            response += "... But Aru thinks yes!" if random.randint(0,1) == 1 else "... But Aru thinks not!"

    if isinstance(ctx, lightbulb.PrefixContext):
        await plugin.app.rest.create_message(content = response, channel = ctx.get_channel(), reply = ctx.event.message)
    else:
        await ctx.respond(f"{ctx.author.mention} asked: \"{ctx.options.question}\"" + f"\n{response}")

def load(bot):
    bot.add_plugin(plugin)