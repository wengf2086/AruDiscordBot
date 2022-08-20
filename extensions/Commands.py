from asyncio.windows_events import NULL
import hikari
import lightbulb
import re
import random
import datetime
import os.path
import requests
from bs4 import BeautifulSoup

plugin = lightbulb.Plugin('Commands')



kirby_react_preset = "<a:kirbeats:1009554827098988574> <a:kirbeatsfast:1009554827992383528> <a:kirbydance:1009554839602204712> <a:kirbydance2:1009554838692044900> <a:kirbyfortnitedance:1009554841963606146> <a:kirbyhi:1009554846967414874> <a:kirbybye:1009554837064650923> <a:kirbyyay:1009554865145528501> <a:kirbyok:1009554850914242754><a:kirbylink:1009554849131675808> <a:kirbyroll:1009554852046700644> <a:kirbyrun:1009554853091082240> <a:kirbyshock:1009554854215168050> <a:kirbyspin:1009554856194867205> <a:kirbyswim:1009554860489842750> <a:kirbyuwu:1009554861739749478> <a:kirbywave:1009554864285683824> <:kirbo:1009554829141606490> <:kirby:1009554833478537377> <:kirbybuffed:1009554836255166474>"
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

# Method that extracts a gif from a URL
def extract_gif_link_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="html.parser")
    metas = soup.find_all(property='og:url')

    for meta in metas:
        if meta.attrs.get("content").endswith(".gif"):
            return meta.attrs.get("content")
    
    return -1 

# Command that allows the user to add a gif/gifs to a certain action
@plugin.command
@lightbulb.option('gif_link', 'link(s) of GIF(s) to be added. Add a space between each link!', type = str)
@lightbulb.option('action', 'action to add the GIF to', type = str)
@lightbulb.command('addaction', 'Add a GIF link for an action command. If you add something sus, you will be blacklisted.')
@lightbulb.implements(lightbulb.SlashCommand)
async def add_action(ctx):
    user_id = ctx.author
    file_name = action_files.get(ctx.options.action)
    f = open(file_name, 'a')

    gif_links = ctx.options.gif_link.split()
    broken_gif_links = []
    for link in gif_links:
        revised_gif_link = link
        if not revised_gif_link.endswith(".gif"): # if url does not end with ".gif", extract gif link from URL
            revised_gif_link = extract_gif_link_from_url(revised_gif_link)
        
        if revised_gif_link == -1: # if gif link is broken
            broken_gif_links.append(revised_gif_link)
        
        else:
            new_line = str(datetime.datetime.now())[:-7] + '|' + str(ctx.author.id) + '|' + revised_gif_link
            f.write(new_line)
            f.write('\n')
    f.close()

    broken_gif_links_string = ""
    for link in broken_gif_links:
        broken_gif_links_string += f"{link}\n"

    if len(gif_links) == 1:
        if len(broken_gif_links) > 0:
            await ctx.respond("Error: GIF URL invalid. Please try another URL.", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)
        else:
            await ctx.respond("GIF successfully added. Thank you for your contribution! ❤️", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)
    elif len(gif_links) > 1:
        if len(broken_gif_links) == len(gif_links):
            await ctx.respond("Error: No GIFs added. Please make sure your URLs are valid.", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)
        elif len(broken_gif_links) > 0:
            await ctx.respond("Error: Only some of the GIFs were added. The following provided URLs could not be added: {broken_gif_links_string}", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)
        else:
            await ctx.respond("GIFs successfully added. Thank you for your contribution! ❤️", flags = hikari.MessageFlag.EPHEMERAL, delete_after = 1)

@plugin.command 
@lightbulb.command('action', 'Specify another user to interact with them with these commands!')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def social_action(ctx):
    pass

# Method called by all action commands
async def perform_action(ctx, action_name, action_string, response_text):
    gif_file = action_files.get(action_name)

    #gif file does not exist. Send error message and return
    if not os.path.exists(gif_file):
        await ctx.respond(f"Error: No GIFs available for this action! Add your own using the `/addaction` command! :3c", flags = hikari.MessageFlag.EPHEMERAL)
        return

    random_gif = random.choice(list(open(gif_file))).split("|")
    gif_author = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = int(random_gif[1]))
    actor_member = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = ctx.author)
    recipient_member = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = ctx.options.user)
    
    embed = hikari.Embed(color = hikari.Color(0xc38ed5))
    embed.set_image(random_gif[2])

    msg = await plugin.app.rest.create_message(channel = ctx.get_channel(), content = f"{recipient_member.mention}{action_string}{actor_member.mention}!" , embed = embed)

    # Report function
    await ctx.respond(f"{response_text} This GIF was added by {gif_author.mention} at `{random_gif[0]}`. If this gif is inappropriate, offensive, or broken, report it by adding the :warning: reaction.", flags = hikari.MessageFlag.EPHEMERAL)

@social_action.child
@lightbulb.option('user', 'Mention the user you want to bonk!', type = hikari.User)
@lightbulb.command('bonk', 'Bonk another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_bonk(ctx):
    await perform_action(ctx, "bonk", ", you have been bonked by ", "BONK!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to blush at!', type = hikari.User)
@lightbulb.command('blush', 'Blush at another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_blush(ctx):
    await perform_action(ctx, "blush", "... \"You're making me blush!\" - ", "uwu..")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to cuddle!', type = hikari.User)
@lightbulb.command('cuddle', 'Cuddle another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_cuddle(ctx):
    await perform_action(ctx, "cuddle", ", you have been cuddled by ", "uwu cuddley wuddley...")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to high five!', type = hikari.User)
@lightbulb.command('highfive', 'High five another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_highfive(ctx):
    await perform_action(ctx, "highfive", ", you have been high fived by ",  "✋")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to hold hands with!', type = hikari.User)
@lightbulb.command('holdhands', 'Hold hands with another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_holdhands(ctx):
    await perform_action(ctx, "holdhands", " is holding hands with ", "H-how lewd..!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to hug!', type = hikari.User)
@lightbulb.command('hug', 'Hug another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_hug(ctx):
    await perform_action(ctx, "hug", ", you have been hugged by ", "Aww!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to kiss!', type = hikari.User)
@lightbulb.command('kiss', 'Kiss another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_kiss(ctx):
    await perform_action(ctx, "kiss", ", you have been kissed by ", "H-how lewd..!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to nom!', type = hikari.User)
@lightbulb.command('nom', 'Nom another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_nom(ctx):
    await perform_action(ctx, "nom", ", you have been nommed by ", "Yummy!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to nuzzle!', type = hikari.User)
@lightbulb.command('nuzzle', 'Nuzzle another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_nuzzle(ctx):
    await perform_action(ctx, "nuzzle", ", you have been nuzzled by ", "uwu..")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to pat!', type = hikari.User)
@lightbulb.command('pat', 'Pat another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_pat(ctx):
    await perform_action(ctx, "pat", ", you have been patted by ", "It'll be okay!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to poke!', type = hikari.User)
@lightbulb.command('poke', 'Poke another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_poke(ctx):
    await perform_action(ctx, "poke", ", you have been poked by ", "Boop!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to slap!', type = hikari.User)
@lightbulb.command('slap', 'Slap another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_slap(ctx):
    await perform_action(ctx, "slap", ", you have been slapped by ", "Ouch!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to stare at!', type = hikari.User)
@lightbulb.command('stare', 'Stare at another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_stare(ctx):
    await perform_action(ctx, "stare", ", you are being stared at by ", "👀")



def load(bot):
    bot.add_plugin(plugin)