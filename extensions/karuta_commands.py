import hikari
import lightbulb

plugin = lightbulb.Plugin('karuta_commands')

# Commands
@plugin.command
@lightbulb.command('karuta_codes', 'Gets codes from a message.')
@lightbulb.implements(lightbulb.PrefixCommand)
async def get_karuta_codes(ctx):
    lines = ctx.event.message.referenced_message.embeds[0].description.split("\n")
    if "✧" in lines[2] or "♡" in lines[2]:
        card_code_pos = 1
    else:
        card_code_pos = 0

    response = ""
    for line in lines:
        components = line.split("·")
        if len(components) > 1:
            card_code = components[card_code_pos].split("`")
            response += card_code[1] +", "
    
    await ctx.respond(response[:-2], reply = ctx.event.message)
        
def load(bot):
    bot.add_plugin(plugin)
