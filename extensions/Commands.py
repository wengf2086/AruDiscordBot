from asyncio.windows_events import NULL
import hikari
import lightbulb
import re
import random
import datetime
import requests
from bs4 import BeautifulSoup

plugin = lightbulb.Plugin('Commands')
kirby_react_preset = "<a:kirbeats:1009554827098988574> <a:kirbeatsfast:1009554827992383528> <a:kirbydance:1009554839602204712> <a:kirbydance2:1009554838692044900> <a:kirbyfortnitedance:1009554841963606146> <a:kirbyhi:1009554846967414874> <a:kirbybye:1009554837064650923> <a:kirbyyay:1009554865145528501> <a:kirbyok:1009554850914242754><a:kirbylink:1009554849131675808> <a:kirbyroll:1009554852046700644> <a:kirbyrun:1009554853091082240> <a:kirbyshock:1009554854215168050> <a:kirbyspin:1009554856194867205> <a:kirbyswim:1009554860489842750> <a:kirbyuwu:1009554861739749478> <a:kirbywave:1009554864285683824> <:kirbo:1009554829141606490> <:kirby:1009554833478537377> <:kirbybuffed:1009554836255166474>"

action_files = {
        'bonk':'action_bonk_gifs.txt',
        'blush': 'action_blush_gifs.txt',
        'cuddle': 'action_cuddle_gifs.txt',
        'highfive': 'action_highfive_gifs.txt',
        'holdhands': 'action_holdhands_gifs.txt',
        'hug': 'action_hug_gifs.txt',
        'kiss': 'action_kiss_gifs.txt',
        'nom': 'action_nom_gifs.txt',
        'nuzzle': 'action_nuzzle_gifs.txt',
        'pat': 'action_pat_gifs.txt',
        'poke': 'action_poke_gifs.txt',
        'slap': 'action_slap_gifs.txt',
        'stare': 'action_stare_gifs.txt', 
    }

# Command functions
@plugin.command
@lightbulb.option('emojis', 'emojis / preset to be used as reactions. Only default emojis and emojis from this server allowed.', type = str, required = True)
@lightbulb.option('message_id', 'ID of the message to be bombed. Will bomb most recent message if not specified.', required = False)
@lightbulb.command('reactbomb', '\'Bombs\' a message with a bunch of (MAX: 20) reactions! emoji presets: \'kirby\'', auto_defer = True)

@lightbulb.implements(lightbulb.SlashCommand)
async def reactbomb(ctx):
    message = ""
    if ctx.options.message_id:
        message = ctx.options.message_id
    else:
        channel = await plugin.app.rest.fetch_channel(channel = ctx.channel_id)
        message = channel.last_message_id

    emojis = ""
    if ctx.options.emojis == "kirby":
        emojis = kirby_react_preset

    elif ctx.options.emojis:
        emojis = ctx.options.emojis

    print(emojis.split(" "))
    for emoji_str in emojis.split(" "):
        emoji = hikari.Emoji.parse(emoji_str)
        await plugin.app.rest.add_reaction(channel = ctx.channel_id, message = message, emoji = emoji)

    await ctx.respond("Success!", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

# Social Actions
# Method that extracts a gif from a URL
def extract_gif_link_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="html.parser")
    metas = soup.find_all(property='og:url')

    for meta in metas:
        if meta.attrs.get("content").endswith(".gif"):
            return meta.attrs.get("content")
    
    return -1 

# Command that allows the user to add a gif to a certain action
@plugin.command
@lightbulb.option('gif_link', 'GIF link to be added', type = str)
@lightbulb.option('action', 'action to add the GIF to', type = str)
@lightbulb.command('addaction', 'Add a GIF link for an action command. If you add something sus, you will be blacklisted.')
@lightbulb.implements(lightbulb.SlashCommand)
async def add_action(ctx):
    revised_gif_link = ctx.options.gif_link
    if not ctx.options.gif_link.endswith(".gif"):
        revised_gif_link = extract_gif_link_from_url(ctx.options.gif_link)
    
    if revised_gif_link == -1:
        await ctx.respond("Error: Invalid GIF link. Please try again.", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)
        return
    
    user_id = ctx.author
    file_name = action_files.get(ctx.options.action)
    f = open(file_name, 'a')
    new_line = str(datetime.datetime.now())[:-7] + '|' + str(ctx.author.id) + '|' + revised_gif_link + '\n'
    f.write(new_line)
    f.close()
    await ctx.respond("GIF successfully added. Thank you for your contribution! ❤️", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@plugin.command 
@lightbulb.command('action', 'Specify another user to interact with them with these commands!')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def social_action(ctx):
    pass

# Method called by all action commands
async def perform_action(ctx, action_name, action_string):
    random_gif = random.choice(list(open(action_files.get(action_name)))).split("|")
    gif_author = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = int(random_gif[1]))
    actor_member = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = ctx.author)
    recipient_member = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = ctx.options.user)
    
    embed = hikari.Embed(color = hikari.Color(0xc38ed5))
    embed.set_image(random_gif[2])
    embed.set_footer(f'This GIF was added by {gif_author.mention} at {random_gif[0]}. If this GIF inappropriate? If so, report it with the <> reaction.')

    await plugin.app.rest.create_message(channel = ctx.get_channel(), content = f"{recipient_member.mention}{action_string}{actor_member.mention}!" , embed = embed)  

@social_action.child
@lightbulb.option('user', 'Mention the user you want to bonk!', type = hikari.User)
@lightbulb.command('bonk', 'Bonk another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_bonk(ctx):
    await perform_action(ctx, "bonk", ", you have been bonked by ")
    await ctx.respond("BONK!", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to blush at!', type = hikari.User)
@lightbulb.command('blush', 'Blush at another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_blush(ctx):
    await perform_action(ctx, "blush", "... \"You're making me blush!\" - ")
    await ctx.respond("uwu..", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to cuddle!', type = hikari.User)
@lightbulb.command('cuddle', 'Cuddle another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_cuddle(ctx):
    await perform_action(ctx, "cuddle", ", you have been cuddled by ")
    await ctx.respond("Cuddley wuddley uwu..", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to high five!', type = hikari.User)
@lightbulb.command('highfive', 'High five another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_highfive(ctx):
    await perform_action(ctx, "highfive", ", you have been high fived by ")
    await ctx.respond("✋", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to hold hands with!', type = hikari.User)
@lightbulb.command('holdhands', 'Hold hands with another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_holdhands(ctx):
    await perform_action(ctx, "holdhands", " is holding hands with ")
    await ctx.respond("How lewd..", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to hug!', type = hikari.User)
@lightbulb.command('hug', 'Hug another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_hug(ctx):
    await perform_action(ctx, "hug", ", you have been hugged by ")
    await ctx.respond("Aww!", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to kiss!', type = hikari.User)
@lightbulb.command('kiss', 'Kiss another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_kiss(ctx):
    await perform_action(ctx, "kiss", ", you have been kissed by ")
    await ctx.respond("How lewd..", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to nom!', type = hikari.User)
@lightbulb.command('nom', 'Nom another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_nom(ctx):
    await perform_action(ctx, "nom", ", you have been nommed by ")
    await ctx.respond("Yummy!", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to nuzzle!', type = hikari.User)
@lightbulb.command('nuzzle', 'Nuzzle another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_nuzzle(ctx):
    await perform_action(ctx, "nuzzle", ", you have been nuzzled by ")
    await ctx.respond(":3c", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to pat!', type = hikari.User)
@lightbulb.command('pat', 'Pat another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_pat(ctx):
    await perform_action(ctx, "pat", ", you have been patted by ")
    await ctx.respond("It'll be okay..", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to poke!', type = hikari.User)
@lightbulb.command('poke', 'Poke another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_poke(ctx):
    await perform_action(ctx, "poke", ", you have been poked by ")
    await ctx.respond("Boop!", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to slap!', type = hikari.User)
@lightbulb.command('slap', 'Slap another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_slap(ctx):
    await perform_action(ctx, "slap", ", you have been slapped by ")
    await ctx.respond("Ouch!", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to stare at!', type = hikari.User)
@lightbulb.command('stare', 'Stare at another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_stare(ctx):
    await perform_action(ctx, "stare", ", you are being stared at by ")
    await ctx.respond("👀", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)



def load(bot):
    bot.add_plugin(plugin)