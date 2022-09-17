import hikari
import lightbulb
import utilities

plugin = lightbulb.Plugin('club_management_commands')

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.option('announcement_channel', "Channel to send actual announcement to. DO NOT SPECIFY if you're testing.", type = hikari.GuildChannel, required = False)
@lightbulb.command('announce', "Send an announcement using Aru. Do not specify announcement_channel parameter when testing.")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def announce(ctx):
    if ctx.options.announcement_channel: # if announcement_channel is specified, Aru will be sending a real announcement to the specified channel (possibly pinging @everyone)
        channel = ctx.options.announcement_channel
        mention_everyone = True
        instructions = f"""
**WARNING: THIS IS THE REAL DEAL. REPLYING TO THIS MESSAGE WILL SEND AN ANNOUNCEMENT TO <#{ctx.options.announcement_channel.id}>**.
__**If your message includes @everyone, it will ping EVERYONE**__.
IF THIS IS YOUR INTENT, PLEASE MAKE SURE THAT THE ANNOUNCEMENT IS PERFECT!

Reply to this message with the message you'd like to announce!
**Put \\`\\`\\` before and after the message.**
To use emojis, use the emoji's mention string but replace `<` with `§`, e.g., `§a:kirbywave:1009321421152981032>`. {utilities.FLAVOR_ARU.get('wink')}
(To get an emoji's mention string, type :emoji_name:)
Example Usage: """

    else: # Aru is sending a test announcement to the current channel (will not ping @everyone)
        mention_everyone = False
        channel = ctx.channel_id
        instructions = f"""
This is just a draft announcement, and will be sent in this channel (<#{ctx.channel_id}>). Even if your message includes @everyone, it won't actually ping @everyone. Trust. :)

Reply to this message with the message you'd like to announce!
**Put \\`\\`\\` before and after the message.**
To use emojis, use the emoji's mention string but replace `<` with `§`, e.g., `§a:kirbywave:1009321421152981032>`. {utilities.FLAVOR_ARU.get('wink')}
(To get an emoji's mention string, type `\`:emoji_name:. If you don't have nitro, this won't work for animated emojis, so you'll have to find someone with nitro or get the mention string some other way. :()
Example Usage: """

    init_msg = await ctx.respond(content = instructions, attachment = 'announce_example.png')

    event = await response_to_message(timeout = 60, initial_message_id = (await init_msg.message()).id)
            
    if event != -1:
        content = str(event.message.content.replace("§","<")[4:-3])

        if (len(content) < 7): # content is too short!
            await plugin.app.rest.create_message(channel = ctx.channel_id, content = "Error: Announcement is too short. Did you put \\`\\`\\` before and after your message? :x", reply = event.message)
            await plugin.app.rest.delete_message(channel = ctx.channel_id, message = await init_msg.message())
            return
            
        await plugin.app.rest.create_message(channel = channel, content = content, mentions_everyone = mention_everyone, attachments = event.message.attachments)
        await plugin.app.rest.delete_message(channel = ctx.channel_id, message = event.message)

    else:
        await plugin.app.rest.create_message(channel = ctx.channel_id, content = "Interation timed out. You took too long! If you still want to send an announcement, please call the command again.")
        await plugin.app.rest.delete_message(channel = ctx.channel_id, message = await init_msg.message())
    
async def response_to_message(timeout, initial_message_id):
    '''Returns Guild Message Create event, or -1 if interaction times out.'''

    try:
        event = await plugin.bot.wait_for(hikari.GuildMessageCreateEvent, timeout, (lambda event: event.message.type == hikari.MessageType.REPLY and event.message.message_reference.id == initial_message_id and event.author_id == 173555466176036864))
        return event
    except:
        return -1

def load(bot):
    bot.add_plugin(plugin)