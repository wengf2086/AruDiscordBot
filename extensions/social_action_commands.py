from asyncio.windows_events import NULL
import hikari
import lightbulb
import random
import datetime
import os.path
import requests

from sql_functions import Gif
import utilities

from bs4 import BeautifulSoup

plugin = lightbulb.Plugin('social_action_commands')

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

    pass

# Command that allows the user to add a gif/gifs to a certain action
@plugin.command
@lightbulb.option('gif_link', 'link(s) of GIF(s) to be added. Add a space between each link!', type = str)
@lightbulb.option('action_name', 'action to add the GIF to', autocomplete=True)
@lightbulb.command('addgif', 'Add a GIF link for an action command. If you add something sus, you will be blacklisted.', auto_defer = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def add_gif(ctx):
    action_name = ctx.options.action_name.lower()
    # Check if action name is valid
    if action_name not in list(utilities.ACTIONS.keys()):
        await ctx.respond("Sorry, I couldn't find an action with that name. Please try again! <a:kirbydeeono:1011803865164816384>")
        return

    gif_links = ctx.options.gif_link.split()
    broken_gif_links = []
    already_added_links = []
    added_links = []
    for link in gif_links:
        revised_link = link
        if not link.endswith(".gif"): # if link doesn't end with '.gif', attempt to extract gif from URL
            revised_link = extract_gif_link_from_url(link)
    
        if revised_link == -1: # link is broken
            broken_gif_links.append(link)

        else: # if not broken
            if Gif.get_gif_from_link(revised_link): # link is already in the database
                already_added_links.append(link)

            else: # if not in the database, add it
                Gif.add_gif(action_name=action_name, author_id=ctx.author.id, gif_link=revised_link)
                added_links.append(link)

    response = ""
    broken_gif_links_string = "\n".join(broken_gif_links)
    already_added_links_string = "\n".join(already_added_links)
    added_links_string = "\n".join(added_links)
    if len(added_links) > 0:
        response += f"\nThe following URL(s) have successfully been added to the database for the `{action_name}` command:\n{added_links_string}\nThank you so much for your contribution! <:kirbyblowkiss:1011481542712897548>"
    if len(already_added_links) > 0:
        response += f"\n\nThe following URL(s) have already been added to the database by another user:\n{already_added_links_string}\nGood taste! <a:kirbywink:1011481550577213450>"
    if len(broken_gif_links) > 0:
        response += f"\n\nThe following URL(s) could not be added:\n{broken_gif_links_string}\nPlease check to make sure the URLs are valid and try again! <a:kirbydeeono:1011803865164816384>"  

    if response == "":
        await ctx.respond("A strange error occurred... Please contact the developer.")

    await ctx.respond(response)

@plugin.command 
@lightbulb.option('user', 'Mention the user you want to bonk!', type = hikari.User)
@lightbulb.option('action_name', "Choose the action you want to use!", autocomplete=True)
@lightbulb.command('action', 'Get a random anime GIF of an action and direct it at another user!')
@lightbulb.implements(lightbulb.SlashCommand)
async def action(ctx):
    action_name = ctx.options.action_name.lower()
    # Check if action name is valid
    if action_name not in list(utilities.ACTIONS.keys()):
        await ctx.respond("Sorry, I couldn't find an action with that name. Please try again! <a:kirbydeeono:1011803865164816384>")
        return

    actor = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = ctx.author)
    recipient = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = ctx.options.user)

    action_string = utilities.ACTIONS.get(action_name).format(recipient = recipient.mention, actor = actor.mention)

    gif = Gif.get_random_gif(action_name = action_name)
    embed = hikari.Embed(color = hikari.Color(0xc38ed5)).set_image(gif.link)

    author = await plugin.app.rest.fetch_user(gif.author_id)
    msg = await plugin.app.rest.create_message(channel = ctx.get_channel(), content = action_string, embed = embed, user_mentions=True)

    # button = plugin.app.rest.build_action_row().add_button(2, f"report|{msg.id}").set_emoji(hikari.Emoji.parse("⚠️")).set_label("Report this GIF").add_to_container()
    await ctx.respond(f"This GIF was added by {author.mention} at `{gif.date_added}`.", flags = hikari.MessageFlag.EPHEMERAL)
    # await respond_to_interaction(20)

    if recipient.id == 1009180210823970956:
        await ctx.respond(attachment = 'action_response.png')

@add_gif.autocomplete("action_name")
@action.autocomplete("action_name")
async def action_autocomplete(opt: hikari.AutocompleteInteractionOption, inter: hikari.AutocompleteInteraction) -> None:
    matching = []
    for action in list(utilities.ACTIONS.keys()):
        if action.startswith(opt.value):
            matching.append(action)
    return matching
 
async def respond_to_interaction(timeout):
    try:
        event = await plugin.bot.wait_for(hikari.InteractionCreateEvent, timeout = timeout)
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
            await respond_to_interaction(20)
        
         elif(custom_id[0] == "report_reason"):
            f = open(utilities.LOG_FILE_NAME, 'a')
            new_line = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '|' + str(event.interaction.user.id) + '|' + event.interaction.values[0] + '|' + custom_id[1] + '\n'
            f.write(new_line)
            f.close()
            await event.interaction.create_initial_response(response_type = 4, content = "Your response has been recorded and will be reviewed. Thank you for your input.", flags = hikari.MessageFlag.EPHEMERAL)

def load(bot):
    bot.add_plugin(plugin)