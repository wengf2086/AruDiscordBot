import hikari
import lightbulb
import requests
from bs4 import BeautifulSoup
import utilities
import sql_functions

plugin = lightbulb.Plugin('database_commands')

@plugin.command 
@lightbulb.command('db', 'Fetch/Modify data in the database.')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def fetch_database(ctx):
    pass

@fetch_database.child
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option('type','Fetch feedback of a specific type.', required = False)
@lightbulb.option('date','Fetch feedback made on a specific date.', required = False)
@lightbulb.option('today_only','Only fetch feedback made today.', type = bool, required = False)
@lightbulb.option('author_id','Fetch feedback made by a specific user.', required = False)
@lightbulb.command('feedback', 'Fetch feedback from the database.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def fetch_feedback(ctx):
    if ctx.options.today_only:
        feedback = sql_functions.fetch_todays_feedback(ctx.options.type, ctx.options.author_id)
    else:
        feedback = sql_functions.fetch_feedback(ctx.options.type, ctx.options.date, ctx.options.author_id)

    await ctx.respond("Fetching feedback...")
    for f in feedback:
        await plugin.app.rest.create_message(channel = ctx.channel_id, content = f"`{f}`")
    await plugin.app.rest.create_message(channel = ctx.channel_id, content = f"All feedback successfully fetched.")

@fetch_database.child
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option('category','Fetch gifs from a specific category', required = False)
@lightbulb.command('gifs', 'Fetch gifs from the database.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def fetch_gifs(ctx):
    if ctx.options.category:
        gifs = sql_functions.fetch_gifs(ctx.options.category)
    else:
        gifs = sql_functions.fetch_all_gifs()

    await ctx.respond("""
Fetching GIFS...\n
Format: (category_name, date_added, author_id, gif_link, appearances, likes, dislikes, reports, is_disabled)
""")
    for g in gifs:
        await plugin.app.rest.create_message(channel = ctx.channel_id, content = f"`{g}`")
    await plugin.app.rest.create_message(channel = ctx.channel_id, content = f"All GIFs successfully fetched.")

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

@fetch_database.child
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option('gif_link', "Enter the gif link you wish to disable.")
@lightbulb.command('disable_gif', '[ADMIN ONLY] Disable an action GIF for the /action command.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def disable_gif(ctx):

    link = ctx.options.gif_link
    if not link.endswith(".gif"): 
        link = extract_gif_link_from_url(link)
    gif = sql_functions.Gif.get_gif_from_link(link)
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

def load(bot):
    bot.add_plugin(plugin)