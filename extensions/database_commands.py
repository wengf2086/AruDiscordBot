import hikari
import lightbulb
import utilities
import sql_functions

plugin = lightbulb.Plugin('database_commands')

@plugin.command 
@lightbulb.command('fetch_database', 'Fetch data from the database.')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def fetch_database(ctx):
    pass

@fetch_database.child
@lightbulb.option('type','Fetch feedback of a specific type.', required = False)
@lightbulb.option('date','Fetch feedback made on a specific date.', required = False)
@lightbulb.option('today_only','Only fetch feedback made today.', type = bool, required = False)
@lightbulb.option('author_id','Fetch feedback made by a specific user.', required = False)
@lightbulb.command('feedback', 'Fetch feedback from the database.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def fetch_feedback(ctx):
    if ctx.options.today_only:
        feedback = sql_functions.fetch_todays_feedback(ctx.options.type, ctx.options.date, ctx.options.author_id)
    else:
        feedback = sql_functions.fetch_feedback(ctx.options.type, ctx.options.date, ctx.options.author_id)

    ret = ""
    for f in feedback:
        ret += f"{f}"
        ret += "\n"

    await ctx.respond(ret)
    
