from asyncio.windows_events import NULL
from dataclasses import is_dataclass
import hikari
import lightbulb
import re
import random
import datetime
import os.path
import requests
from bs4 import BeautifulSoup
import auxiliary

plugin = lightbulb.Plugin('social_action_commands')
log_file_name = "log.txt"

# Social Actions

# Method that extracts a gif from a URL
def extract_gif_link_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features="html.parser")
        metas = soup.find_all(property='og:url')

        for meta in metas:
            if meta.attrs.get("content").endswith(".gif"):
                return meta.attrs.get("content")
        return -1
    except:
        return -1 

@plugin.command 
@lightbulb.command('action', 'Get a random anime GIF of an action and direct it to another user!')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def social_action(ctx):
    pass

# Command that allows the user to add a gif/gifs to a certain action
@social_action.child
@lightbulb.option('gif_link', 'link(s) of GIF(s) to be added. Add a space between each link!', type = str)
@lightbulb.option('action', 'action to add the GIF to', type = str)
@lightbulb.command('addgif', 'Add a GIF link for an action command. If you add something sus, you will be blacklisted.', auto_defer = True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add_gif(ctx):
    if ctx.options.action not in auxiliary.get_all_action_names():
        await ctx.respond("Sorry, I couldn't find an action with that name. Please try again! <a:kirbydeeono:1011803865164816384>")
        return

    action_file_name = "C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/" + f"action_{ctx.options.action}_gifs.txt"
    
    gif_links = ctx.options.gif_link.split()
    broken_gif_links = []
    already_added_links = []
    added_links = []
    for link in gif_links:
        revised_gif_link = link
        if not revised_gif_link.endswith(".gif"): # if url does not end with ".gif", extract gif link from URL
            revised_gif_link = extract_gif_link_from_url(revised_gif_link)
        
        if revised_gif_link == -1: # if gif link is broken
            broken_gif_links.append("<a:purpleheart:1012784670687100999> `" + str(link) + "`")
        
        else:
            with open(action_file_name) as f:
                if revised_gif_link in f.read():
                    already_added_links.append("<a:purpleheart:1012784670687100999> `" + str(revised_gif_link) + "`")
                
                else:
                    new_line = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '|' + str(ctx.author.id) + '|' + revised_gif_link
                    with open(action_file_name, 'a') as f:
                        f.write(new_line + '\n')
                    added_links.append("<a:purpleheart:1012784670687100999> `" + str(revised_gif_link) + "`")

    broken_gif_links_string = "\n".join(broken_gif_links)
    already_added_links_string = "\n".join(already_added_links)
    added_links_string = "\n".join(added_links)

    response = ""
    if len(added_links) > 0:
        response += f"\nThe following URL(s) have successfully been added to the database for the `{ctx.options.action}` command:\n{added_links_string}\nThank you so much for your contribution! <:kirbyblowkiss:1011481542712897548>"
    if len(already_added_links) > 0:
        response += f"\n\nThe following URL(s) have already been added to the database by another user:\n{already_added_links_string}\nGood taste! <a:kirbywink:1011481550577213450>"
    if len(broken_gif_links) > 0:
        response += f"\n\nThe following URL(s) could not be added:\n{broken_gif_links_string}\nPlease check to make sure the URLs are valid and try again! <a:kirbydeeono:1011803865164816384>"    

    await ctx.respond(response)

# Method called by all action commands
async def perform_action(ctx, action_name, action_string, response_text):
    gif_file = "C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/" + f"action_{action_name}_gifs.txt"

    #gif file does not exist. Send error message and return
    if not os.path.exists(gif_file):
        await ctx.respond(f"Error: No GIFs available for this action! Add your own using the `/addaction` command! :3c", flags = hikari.MessageFlag.EPHEMERAL)
        return

    random_gif = random.choice(list(open(gif_file))).split("|")
    gif_author = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = int(random_gif[1]))
    actor_member = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = ctx.author)
    recipient_member = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = ctx.options.user)
    
    embed = hikari.Embed(color = hikari.Color(0xc38ed5)).set_image(random_gif[2])

    msg = await plugin.app.rest.create_message(channel = ctx.get_channel(), content = f"{recipient_member.mention}{action_string}{actor_member.mention}!" , embed = embed, user_mentions=True)

    # Report function
    button = plugin.app.rest.build_action_row().add_button(2, f"report|{msg.id}").set_emoji(hikari.Emoji.parse("⚠️")).set_label("Report this GIF").add_to_container()
    await ctx.respond(f"{response_text} This GIF was added by {gif_author.mention} at `{random_gif[0]}`.", component = button, flags = hikari.MessageFlag.EPHEMERAL)
    await respond_to_interaction()

async def respond_to_interaction():
    try:
        event = await plugin.bot.wait_for(hikari.InteractionCreateEvent, timeout = 10)
    except:
        print("Interaction Time-Out. Perfectly Normal :)")
        return

    if event.interaction.type == 3: # if interaction is of type MESSAGE_COMPONENT
         custom_id = event.interaction.custom_id.split("|")
         if(custom_id[0] == "report"):
            msg = await plugin.app.rest.fetch_message(channel = event.interaction.channel_id, message = custom_id[1])

            embed_description = "Reporting a GIF will mark it for review. \nIf the GIF is deemed inappropriate after review, it will be removed.\nIf you're sure you'd like to report this GIF, select the reason below."
            embed = hikari.Embed(color = hikari.Color(0xc38ed5), title = "Report a GIF",description = embed_description).set_thumbnail(msg.embeds[0].image).set_footer("Warning: Abusing the 'Report' feature will result in a blacklist. Also, I will be very sad. :(")
            select_menu = plugin.app.rest.build_action_row().add_select_menu(f"report_reason|{msg.embeds[0].image}")\
                .add_option("GIF is NSFW", "NSFW").set_emoji(hikari.Emoji.parse("🔞")).set_description("The GIF is overly sexual or inappropriate.").add_to_menu()\
                .add_option("GIF is in the wrong category", "Wrong_Category").set_emoji(hikari.Emoji.parse("❌")).set_description("The GIF is not of the correct action.").add_to_menu()\
                .add_option("GIF is not loading", "Broken").set_emoji(hikari.Emoji.parse("🛠️")).set_description("The GIF is not loading properly.").add_to_menu()\
                .add_to_container()
            await event.interaction.create_initial_response(response_type = 4, content = "Are you sure you want to report this GIF?", flags = hikari.MessageFlag.EPHEMERAL, component = select_menu, embed = embed)
            await respond_to_interaction()
        
         elif(custom_id[0] == "report_reason"):
            f = open(log_file_name, 'a')
            new_line = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '|' + str(event.interaction.user.id) + '|' + event.interaction.values[0] + '|' + custom_id[1] + '\n'
            f.write(new_line)
            f.close()
            await event.interaction.create_initial_response(response_type = 4, content = "Your response has been recorded and will be reviewed. Thank you for your input.", flags = hikari.MessageFlag.EPHEMERAL)

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
@lightbulb.option('user', 'Mention the user you want to kick!', type = hikari.User)
@lightbulb.command('kick', 'Kick another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_kick(ctx):
    await perform_action(ctx, "kick", ", you have been kicked by ", "Ouch!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to kiss!', type = hikari.User)
@lightbulb.command('kiss', 'Kiss another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_kiss(ctx):
    await perform_action(ctx, "kiss", ", you have been kissed by ", "H-how lewd..!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to laugh at!', type = hikari.User)
@lightbulb.command('laugh', 'Laugh at another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_laugh(ctx):
    await perform_action(ctx, "laugh", ", you are being laughed at by ", "Haha!")

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
@lightbulb.option('user', 'Mention the user you want to punch!', type = hikari.User)
@lightbulb.command('punch', 'Punch at another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_punch(ctx):
    await perform_action(ctx, "punch", ", you have been punched by ", "<a:kirbypunch:1011814450757636137>")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to poke!', type = hikari.User)
@lightbulb.command('poke', 'Poke another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_poke(ctx):
    await perform_action(ctx, "poke", ", you have been poked by ", "Boop!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to shoot!', type = hikari.User)
@lightbulb.command('shoot', 'Shoot another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_shoot(ctx):
    await perform_action(ctx, "shoot", ", you have been shot by ", "<:kirbygun:1009321446637588480> Bang!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to slap!', type = hikari.User)
@lightbulb.command('slap', 'Slap another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_slap(ctx):
    await perform_action(ctx, "slap", ", you have been slapped by ", "That's gonna sting..!")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to stare at!', type = hikari.User)
@lightbulb.command('stare', 'Stare at another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_stare(ctx):
    await perform_action(ctx, "stare", ", you are being stared at by ", "<a:kirbyshock:1009554854215168050>")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to tickled', type = hikari.User)
@lightbulb.command('tickle', 'Tickle another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_tickle(ctx):
    await perform_action(ctx, "tickle", ", you are being tickled by ", "👐")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to tuck in!', type = hikari.User)
@lightbulb.command('tuckin', 'Tuck in another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_tuckin(ctx):
    await perform_action(ctx, "tuckin", ", you are being tucked in by ", "Sweet dreams... <:kirbysleeby:1009554855293096048>")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to wink at!', type = hikari.User)
@lightbulb.command('wink', 'Wink at another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_wink(ctx):
    await perform_action(ctx, "wink", ", you are being winked at by ", "<a:kirbywink:1011481550577213450>")

@social_action.child
@lightbulb.option('user', 'Mention the user you want to yeet!', type = hikari.User)
@lightbulb.command('yeet', 'Yeet another user!')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def action_yeet(ctx):
    await perform_action(ctx, "yeet", ", you have been yeeted by ", "YEET!")

def load(bot):
    bot.add_plugin(plugin)