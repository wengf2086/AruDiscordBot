import hikari
import lightbulb
import utilities

plugin = lightbulb.Plugin('club_management_commands')

@plugin.command
@lightbulb.command('send_announcement_temp', "ADMIN only. Don't touch.")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def announce_temp(ctx):
    if ctx.author.id != 173555466176036864:
        return
    
    text = f"""Hi `@`everyone! <a:kirbywave:1009321421152981032>
Firstly, welcome to all the new members that joined from ClubFest! We appreciate you showing interest in Club Anime and hope you enjoy your stay. If you haven't joined the club on NYU Engage yet, please do so! That way you'll receive emails from us (and we'll receive more club funds >:)).
I've got some news regarding club meetings that I'm excited to share with y'all:

1. Club Meetings will be on **Fridays**! Note that our In-Person and Online meeting times are different:
- In-Person: `4:30 PM` to `6:30 PM`, Location: `GC 275 (Global Center)`
- Online: `6:00 PM` to `8:00 PM`, on Discord (here!)

2. __Our first meeting is *this* Friday, from `6:00 PM` to `8:00 PM`!__
- It will be **online**, on Discord. Just join the <#752188246217195604> voice channel at 6 PM; you should see some of us already in there.
- We'll be doing introductions and icebreakers... <:kirbyblush:1011482397788885073> , as well as our annual anime + club trivia Kahoot!
- We will be screening two anime shows, both randomly chosen from the suggestions left by new members at Club Fest. If you left an anime suggestion, you should join us and see if your anime was picked <:kirbyhappy:1011482402020921464>

That's all! We also have some other events coming up this month (monthly movie night, first in-person meeting, giveaway event... ?!), so stay tuned for more info. Looking forward to seeing new (and old) members in our first meeting. :)"""

    await plugin.app.rest.create_message(channel = 752193230694645811, content = text)

@plugin.command
@lightbulb.option('announcement_channel', "Channel to send actual announcement to. DO NOT SPECIFY if you're testing.", type = hikari.GuildChannel, required = False)
@lightbulb.command('announce', "ADMIN only. Don't touch.")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def announce(ctx):
    if ctx.author.id != 173555466176036864:
        await ctx.respond("I'm very disappointed in you. Don't try to use admin commands if you're not an admin! >:'C", flags = hikari.MessageFlag.EPHEMERAL)
        return

    if ctx.options.announcement_channel:
        mention_everyone = True
        channel = ctx.options.announcement_channel
        instructions = f"WARNING: THIS IS THE REAL DEAL. REPLYING TO THIS MESSAGE WILL SEND AN ANNOUNCEMENT TO <#{ctx.options.announcement_channel.id}>.\nIf your message includes @everyone, it will ping EVERYONE.\nIF THIS IS YOUR INTENT, PLEASE MAKE SURE THAT THE ANNOUNCEMENT IS PERFECT!\nReply to this message with the message you'd like to announce!\nPut \\`\\`\\` before and after the message.\nTo use emojis, use the whole emoji's mention but replace `<` with `§`, e.g., `§a:kirbywave:1009321421152981032>`. {utilities.FLAVOR_ARU.get('wink')}"
    else:
        mention_everyone = False
        channel = ctx.channel_id
        instructions = f"This is just a draft announcement, and will be sent in this channel. Even if your message includes @everyone, it won't actually ping @everyone. Trust. :)\nReply to this message with the message you'd like to announce!\nPut \\`\\`\\` before and after the message.\nTo use emojis, use the whole emoji's mention but replace `<` with `§`, e.g., `§a:kirbywave:1009321421152981032>`. {utilities.FLAVOR_ARU.get('wink')}"

    init_msg = await ctx.respond(instructions)

    event = await response_to_message(timeout = 30, initial_message_id = (await init_msg.message()).id)
    content = str(event.message.content.replace("§","<")[4:-3])

    if (len(content) < 7): # content is too short!
        await plugin.app.rest.create_message(channel = ctx.channel_id, content = "Error: Announcement is too short. Did you put \\`\\`\\` before and after your message? :x", reply = event.message)
        await plugin.app.rest.delete_message(channel = ctx.channel_id, message = await init_msg.message())
        return
            
    if event != -1:
        await plugin.app.rest.create_message(channel = channel, content = content, mentions_everyone = mention_everyone, attachments = event.message.attachments)

    await plugin.app.rest.delete_message(channel = ctx.channel_id, message = await init_msg.message())
    await plugin.app.rest.delete_message(channel = ctx.channel_id, message = event.message)


async def response_to_message(timeout, initial_message_id):
    '''Returns Guild Message Create event, or -1 if interaction times out.'''

    try:
        event = await plugin.bot.wait_for(hikari.GuildMessageCreateEvent, timeout, (lambda event: event.message.type == hikari.MessageType.REPLY and event.message.message_reference.id == initial_message_id and event.author_id == 173555466176036864))
        return event
    except:
        return -1

def load(bot):
    bot.add_plugin(plugin)

# NOT

# YET

# IMPLEMENTED

# !!!