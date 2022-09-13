import hikari
import lightbulb

plugin = lightbulb.Plugin('channel_management_commands')

@plugin.command
@lightbulb.command('send_announcement', 'ADMIN only. Don't touch.')
@lightbulb.implements(lightbulb.SlashSubCommand, lightbulb.PrefixCommand)
async def command_info(ctx):
    if ctx.author.id != 173555466176036864:
        return
    text = f"""Hi `@`everyone! <a:kirbywave:1009321421152981032>\n
> Firstly, welcome to all the new members that joined from ClubFest! We appreciate you showing interest in Club Anime and hope you enjoy your stay. \n
> I've got some news regarding club meetings that I'm excited to share with you all:\n
> \n
> 1. Club Meetings will be on **Fridays**! Note that our In-Person and Online meeting times are different:\n
> - In-Person: `4:30 PM` to `6:30 PM`, Location: `GC 275 (Global Center)`\n
> - Online: `6:00 PM` to `8:00 PM`, on Discord (here!)\n
> \n
> 2. __Our first meeting is *this* Friday, from `6:00 PM` to `8:00 PM`!__\n
> - It will be **online**, on Discord. Just join the <#752189506916057108>! voice channel at 6 PM; you should see some of us already in there.\n
> - We'll be doing introductions and icebreakers... <:kirbyblush:1011482397788885073> , as well as our annual anime + club trivia Kahoot!\n
> - We will be screening two anime shows, both randomly chosen from the suggestions left by new members at Club Fest. If you left an anime suggestion, you should join us and see if your anime was picked <:kirbyhappy:1011482402020921464> \n
> \n
> That's all! We also have some other events coming up this month (monthly movie night, first in-person meeting, giveaway event... ?!), so stay tuned for more info. Looking forward to seeing new (and old) members in our first meeting. :)"""
    await plugin.app.rest.create_message(channel = 752193230694645811, content = text)

def load(bot):
    bot.add_plugin(plugin)

# NOT

# YET

# IMPLEMENTED

# !!!