import hikari
import lightbulb
import requests
import uuid

import sql_functions
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
    msg = await plugin.app.rest.create_message(channel = ctx.get_channel(), content = action_string, embed = embed, user_mentions=True) # Actually sends the GIF
    gif.incr_appearance() # Increment appearance attribute of the GIF in the database

    gif_info = f"This GIF was added by {author.mention} at `{gif.date_added}`."

    feedback = sql_functions.fetch_todays_feedback(author_id = ctx.author.id) # Get all the feedback sent by the author today
    if ctx.author.id != 173555466176036864 and feedback and len(feedback) >= utilities.DAILY_FEEDBACK_LIMIT: # Daily Interaction Limit Reached, do not allow further feedback.
        await ctx.respond(content = f"{gif_info}\n(*You have reached your maximum feedback limit today. Thanks for your input!*)", flags = hikari.MessageFlag.EPHEMERAL)
        return

    unique_id = str(uuid.uuid1()) # 36 character unique identifier to receive unique interaction responses for this Queue
    buttons = plugin.app.rest.build_action_row()
    buttons.add_button(2, f"upvote|{unique_id}").set_emoji(hikari.Emoji.parse("👍")).add_to_container()
    buttons.add_button(2, f"downvote|{unique_id}").set_emoji(hikari.Emoji.parse("👎")).add_to_container()
    buttons.add_button(2, f"report|{unique_id}").set_emoji(hikari.Emoji.parse("⚠️")).set_label("Report this GIF").add_to_container()

    await ctx.respond(content = gif_info, component = buttons, flags = hikari.MessageFlag.EPHEMERAL)

    if recipient.id == 1009180210823970956: # a quirky response if an action is done to Aru.
        await ctx.respond(attachment = '../images/action_response.png')

    while (event := (await response_to_interaction(30, unique_id))) != -1:
        if event.interaction.custom_id.split("|")[0] == "upvote":
            sql_functions.add_feedback(feedback_type = "upvote", author_id = ctx.author.id, info = gif.link)
            gif.incr_likes()

            buttons = plugin.app.rest.build_action_row()
            buttons.add_button(3, f"complete|{unique_id}").set_emoji(hikari.Emoji.parse("👍")).add_to_container()
            buttons.add_button(2, f"downvote|{unique_id}").set_emoji(hikari.Emoji.parse("👎")).set_is_disabled(True).add_to_container()
            buttons.add_button(2, f"report|{unique_id}").set_emoji(hikari.Emoji.parse("⚠️")).set_label("Report this GIF").set_is_disabled(True).add_to_container()
            await event.interaction.create_initial_response(response_type = 7)
            await ctx.interaction.edit_initial_response(content = f"{gif_info}\nYou upvoted this GIF!", embed = None, component = buttons)

        elif event.interaction.custom_id.split("|")[0] == "downvote":
            sql_functions.add_feedback(feedback_type = "downvote", author_id = ctx.author.id, info = gif.link)
            gif.incr_dislikes()

            buttons = plugin.app.rest.build_action_row()
            buttons.add_button(2, f"upvote|{unique_id}").set_emoji(hikari.Emoji.parse("👍")).set_is_disabled(True).add_to_container()
            buttons.add_button(4, f"complete|{unique_id}").set_emoji(hikari.Emoji.parse("👎")).add_to_container()
            buttons.add_button(2, f"report|{unique_id}").set_emoji(hikari.Emoji.parse("⚠️")).set_label("Report this GIF").add_to_container()
            await event.interaction.create_initial_response(response_type = 7)
            await ctx.interaction.edit_initial_response(content = f"{gif_info}\nYou downvoted this GIF!", embed = None, component = buttons)

        elif event.interaction.custom_id.split("|")[0] == "report":
            embed_description = "Reporting a GIF will delete the message and mark the GIF for review.\nIf the GIF is deemed inappropriate after review, it will be removed.\n\nIf you're sure you'd like to report this GIF, select the reason below, or go back."
            embed = hikari.Embed(color = hikari.Color(0xc38ed5), title = "Are you sure you want to report this GIF?", description = embed_description)\
                .set_thumbnail(msg.embeds[0].image)\
                .set_footer("Warning: Abusing the 'Report' feature will result in a blacklist. Also, I will be very sad. :(")
            select_menu = plugin.app.rest.build_action_row().add_select_menu(f"report_reason|{unique_id}")\
                .add_option("GIF is NSFW", "nsfw").set_emoji(hikari.Emoji.parse("🔞")).set_description("The GIF is overly sexual or inappropriate.").add_to_menu()\
                .add_option("GIF is in the wrong category", "wrong_cat").set_emoji(hikari.Emoji.parse("❌")).set_description("The GIF is not of the correct action.").add_to_menu()\
                .add_option("GIF is not loading", "broken").set_emoji(hikari.Emoji.parse("🛠️")).set_description("The GIF is not loading properly.").add_to_menu()\
                .add_option("Cancel", "Nevermind").set_emoji(hikari.Emoji.parse("⬅️")).set_description("Go back to the previous menu.").add_to_menu()\
                .add_to_container()

            await event.interaction.create_initial_response(response_type = 7)
            await ctx.interaction.edit_initial_response(embed = embed, component = select_menu)

        elif event.interaction.custom_id.split("|")[0] == "report_reason":
            if event.interaction.values[0] == "Nevermind":
                buttons = plugin.app.rest.build_action_row()
                buttons.add_button(2, f"upvote|{unique_id}").set_emoji(hikari.Emoji.parse("👍")).add_to_container()
                buttons.add_button(2, f"downvote|{unique_id}").set_emoji(hikari.Emoji.parse("👎")).add_to_container()
                buttons.add_button(2, f"report|{unique_id}").set_emoji(hikari.Emoji.parse("⚠️")).set_label("Report this GIF").add_to_container()
                await event.interaction.create_initial_response(response_type = 7)
                await ctx.interaction.edit_initial_response(content = gif_info, embed = None, component = buttons)

            else:
                sql_functions.add_feedback(feedback_type = event.interaction.values[0], author_id = ctx.author.id, info = gif.link)
                gif.incr_reports()
                content = f"You reported this GIF for the following reason: `{event.interaction.values[0].upper()}`\nYour feedback has been recorded and will be reviewed. Thank you for your input."

                await event.interaction.create_initial_response(response_type = 7)
                await ctx.interaction.edit_initial_response(content = content, embed = None, component = None)
                await plugin.app.rest.delete_message(channel = ctx.channel_id, message = msg)

@add_gif.autocomplete("action_name")
@action.autocomplete("action_name")
async def action_autocomplete(opt: hikari.AutocompleteInteractionOption, inter: hikari.AutocompleteInteraction) -> None:
    matching = []
    for action in list(utilities.ACTIONS.keys()):
        if action.startswith(opt.value):
            matching.append(action)
    return matching
 
@plugin.command 
@lightbulb.option('gif_link', "Enter the gif link you wish to disable.", autocomplete=True)
@lightbulb.command('disable_gif', '[ADMIN ONLY] Disable an action GIF for the /action command.')
@lightbulb.implements(lightbulb.SlashCommand)
async def disable_gif(ctx):
    if ctx.author.id != 173555466176036864:
        ctx.respond("You don't have permission to use this command.", flags = hikari.MessageFlag.EPHEMERAL)
        return

    link = ctx.options.gif_link
    if not link.endswith(".gif"): # if link doesn't end with '.gif', attempt to extract gif from URL
        link = extract_gif_link_from_url(link)
    gif = Gif.get_gif_from_link(link)
    if gif:
        gif.disable()
        if gif.is_disabled:
            embed = hikari.Embed(title = "Disabled the GIF:", description = link, color = hikari.Color(0xc38ed5)).set_image(link)
            await ctx.respond(embed)
        else:
           embed = hikari.Embed(title = "Enabled the GIF:", description = link, color = hikari.Color(0xc38ed5)).set_image(link)
           await ctx.respond(embed)
    else:
        ctx.respond("Error: GIF not found.")

async def response_to_interaction(timeout, unique_id):
    '''Returns interaction response event, or -1 if interaction times out.'''
    try:
        event = await plugin.bot.wait_for(hikari.InteractionCreateEvent, timeout, (lambda event: event.interaction.type == 3 and event.interaction.custom_id.split("|")[1] == unique_id))
        return event
    except:
        return -1

def load(bot):
    bot.add_plugin(plugin)