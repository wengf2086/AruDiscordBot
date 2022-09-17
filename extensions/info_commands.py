import hikari
import lightbulb
import datetime
import utilities

plugin = lightbulb.Plugin('info_commands')

start_time = None # Calculated when the bot is started. Used to calculate uptime.

@plugin.command 
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.command('info', 'Get info on a user or server.')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def get_info(ctx):
    pass

@get_info.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option('user', 'Mention the user you want to inspect or input their user ID.', type = hikari.User)
@lightbulb.command('user', 'Get info on a user.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get_info_on_user(ctx):
    user = ctx.options.user

    # if the user is a Member, display more information
    if isinstance(user, hikari.Member):

        # get member's presence and visible status
        presence = user.get_presence()
        if presence == None: # If the member has no presence, then the user is offline
            status_string = "Offline"
            status_emoji = utilities.STATUS_EMOJIS.get("offline")
        
        else: # If the user is online
            if presence.visible_status == "online":
                status_string = "Online"
                status_emoji = utilities.STATUS_EMOJIS.get("online")
    
            elif presence.visible_status == "idle":
                status_string = "Idle"
                status_emoji = utilities.STATUS_EMOJIS.get("idle") 
            else: # Member is dnd
                status_string = "Do Not Disturb"
                status_emoji = utilities.STATUS_EMOJIS.get("dnd") 

            # get member's client status
            if presence.client_status.desktop == "offline": # if the user is not on desktop
                if presence.client_status.mobile != "offline": # on mobile
                    status_string += "(Mobile)"
                    if presence.visible_status == "online": # if online, get mobile emoji
                        status_emoji = utilities.STATUS_EMOJIS.get("mobile")

                elif presence.client_status.web != "offline": # on web
                    status_string += "(Web)"
        
        # create a string of the member's roles (excluding @everyone)
        member_roles = await user.fetch_roles()
        roles = f"{''.join([role.mention for role in member_roles if role.name != '@everyone'])}" if len(member_roles) > 1 else "None"

        server_name = f"'{await plugin.app.rest.fetch_guild(user.guild_id)}'" # server name

        embed = hikari.Embed(title = f"Member Information for {user.username}#{user.discriminator}", color = hikari.Color(0xc38ed5))\
            .set_thumbnail(user.avatar_url)\
            .add_field(name = "User", value = f"{user.mention}", inline = True)\
            .add_field(name = "User ID", value = user.id, inline = True)\
            .add_field(name = "Account Created On", value = user.created_at.strftime("%m/%d/%Y, %H:%M:%S"), inline = True)\
            .add_field(name = f"Status {status_emoji}", value = f"{status_string}", inline = True)\
            .add_field(name = "Server Boosting Since", value = user.premium_since if user.premium_since else "Not server boosting", inline = True)\
            .add_field(name = f"Joined {server_name if len(server_name) <= 16 else 'Server'} On", value = user.joined_at.strftime("%m/%d/%Y, %H:%M:%S"), inline = True)\
            .add_field(name = f"Roles ({len(member_roles) - 1})", value = roles, inline = False)

    # if the user is not a Member, but a user
    elif isinstance(ctx.options.user, hikari.User):
        embed = hikari.Embed(title = f"User Information for {user.username}#{user.discriminator}", color = hikari.Color(0xc38ed5))\
            .set_thumbnail(user.avatar_url)\
            .add_field(name = "User", value = f"{user.mention}", inline = False)\
            .add_field(name = "User ID", value = user.id, inline = False)\
            .add_field(name = "Account Created On", value = user.created_at.strftime("%m/%d/%Y, %H:%M:%S"), inline = False)\
            .set_footer("This user is not a member of this server.")\

    # if the user could not be found. This code should not run; Discord makes sure the input is a valid user.
    else:
        ctx.respond("Sorry, I couldn't find that user! Please make sure you are mentioning a user or inputting a user ID.", flags = hikari.MessageFlag.EPHEMERAL)
        return
    
    await ctx.respond(embed = embed)

@get_info.child
@lightbulb.command('server', 'Get info on this server.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get_info_on_server(ctx):
    guild = ctx.get_guild()

    # Count humans, bots, voice channels, and text channels
    bot_count, human_count, voice_count, text_count = 0, 0, 0, 0
    for i in range(0, len(guild.get_members())):
        member = guild.get_members().get_item_at(i)
        if not member.is_bot and not member.is_system:
            human_count += 1
        elif member.is_bot:
            bot_count += 1
    
    for i in range(0, len(guild.get_channels())):
        channel = guild.get_channels().get_item_at(i)
        if isinstance(channel, hikari.GuildVoiceChannel):
            voice_count += 1
        elif isinstance(channel, hikari.GuildTextChannel): 
            text_count += 1

    embed = hikari.Embed(title = f"Server Information for {guild.name}", description = guild.description, color = hikari.Color(0xc38ed5))\
            .set_thumbnail(guild.icon_url)\
            .add_field(name = "Server Owner", value = (await guild.fetch_owner()).mention, inline = True)\
            .add_field(name = "Server ID", value = guild.id, inline = True)\
            .add_field(name = "Server Created On", value = guild.created_at.strftime("%m/%d/%y, %H:%M:%S"), inline = True)\
            .add_field(name = "Member Count", value = f"{guild.member_count} ({human_count} user{'s' if human_count > 1 else ''}, {bot_count} bot{'s' if bot_count > 1 else ''})", inline = True)\
            .add_field(name = "Channel Count", value = f"{voice_count + text_count} ({text_count} text, {voice_count} voice)", inline = True)\
            .add_field(name = "Role Count", value = f"{len(guild.get_roles()) - 1}", inline = True)\
            .add_field(name = "Server Boost Level", value = "No Boosts" if not guild.premium_tier else str(guild.premium_tier).replace("TIER_","Tier ") + " (" + str(guild.premium_subscription_count) + " Boosts)", inline = False)

    await ctx.respond(embed = embed)

@get_info.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option('user', 'Mention the user you want the profile picture of or input their user ID', type = hikari.User, required = False)
@lightbulb.command('avatar', 'Get a user\'s profile picture, or your own!', aliases=["profile", "avatar"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get_profile_picture(ctx):
    if ctx.options.user:
        target = ctx.options.user
        title = f"{target.username}'s Profile Picture"

    else: # If no user is provided, return the author's profile picture
        target = ctx.author
        title = "Your Profile Picture"

    flavor_text = "Wait, that's me! Heehee!" if target.id == 1009180210823970956 else ''
    embed = hikari.Embed(title = title, url = str(target.display_avatar_url), color = hikari.Color(0xc38ed5))\
        .set_image(target.display_avatar_url)\
        .set_footer(icon = plugin.app.get_me().avatar_url, text = f"What a cutie! {flavor_text}")

    await ctx.respond(embed = embed)

@get_info.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.command('help', 'Learn more about me, Aru! :3c')
@lightbulb.implements(lightbulb.SlashSubCommand, lightbulb.PrefixCommand)
async def aru_info(ctx):
    member = ctx.get_guild().get_member(plugin.app.get_me().id)

    creator = await plugin.app.rest.fetch_user(173555466176036864)
    try: # if creator (me) is a member of the guild, mention me
        creator = await plugin.app.rest.fetch_member(guild = ctx.get_guild(), user = 173555466176036864)
        display_creator = creator.mention
    
    except: # otherwise just print my username
        display_creator = creator.username + "#" + creator.discriminator
    
    server_name = f"'{await plugin.app.rest.fetch_guild(member.guild_id)}'"

    pretext = f"Hi, I'm {member.mention}. "
    if member.display_name != member.username:
        pretext += "Wait, did someone change my name...? Anyways, my _real_ name is Aru. "
    pretext += f"Nice to meet you! {utilities.FLAVOR.get('greeting_1')}"
    description = pretext + ""
    uptime = (datetime.datetime.now() - start_time).total_seconds()
    uptime_days = int(uptime // 86400)
    uptime -= uptime_days * 86400
    uptime_hours = int(uptime // 3600)
    uptime -= uptime_hours * 3600
    uptime_minutes = int(uptime // 60)
    uptime -= uptime_minutes * 60
    uptime_seconds = int(uptime)

    # Action Commands Info
    action_names_string = f"{' '.join(['`' + action_name + '`' for action_name in list(utilities.ACTIONS.keys())])}"
    info_action_name = f"{utilities.FLAVOR.get('exclamation')} /action commands:"
    info_action_value = f"Get a random anime GIF of a specific action and direct it towards another user!\
                          \n{action_names_string}\
                          \n\nDid you know you can add your own GIFs? Find out how:\
                          \n`/info command addgif`"

    # Fun Commands Info
    info_fun_name = f"{utilities.FLAVOR.get('tongue')} /fun commands:"
    info_fun_value = "Miscellaneous commands that do random fun things!"
    info_fun_value += "\n`reactbomb`: Adds multiple (max: 20) emojis to a message."
    info_fun_value += "\n\n`8ball`: Ask the Magic 8-Ball™ a yes/no question!"
    
    # Info Commands... Info
    info_info_name = f"{utilities.FLAVOR.get('question')} /info commands:"
    info_info_value = "Get info about a user, this server, me, or a specific command!\
                       \n`user` `server` `avatar` `help` `command`"

    # Music Commands Info
    info_music_name = f"{utilities.FLAVOR.get('music')} Music commands: (Renovation in progress)"
    info_music_value = "Play music!\
                        \n`play` `stop` `pause` `resume` `seek` `queue` `np` `move` `remove` `repeat` `shuffle` `leave`"

    # Feedback Command Info
    info_feedback_name = f"{utilities.FLAVOR.get('lightbulb')} Got a question, comment, or suggestion?"
    info_feedback_value = "Let your heart out with the `/feedback` command. I'll listen to whatever you have to say... "
    
    # create embed to display information
    await ctx.respond(hikari.Embed(title = f"{utilities.FLAVOR.get('greeting_2')} About Me", description = description, color = hikari.Color(0xc38ed5))\
        .set_thumbnail(member.avatar_url)\
        .add_field(name = f"{utilities.FLAVOR.get('primary_option')} Joined {server_name if len(server_name) <= 16 else 'Server'} On", value = str(member.joined_at)[:19], inline = True)\
        .add_field(name = f"{utilities.FLAVOR.get('primary_option')} Total Server Count", value = f"Currently in {len(utilities.SERVERS)} servers", inline = True)\
        .add_field(name = f"{utilities.FLAVOR.get('primary_option')} My User ID", value = member.id, inline = False)\
        .add_field(name = f"{utilities.FLAVOR.get('primary_option')} My Birthday", value = str(member.created_at)[:19], inline = True)\
        .add_field(name = f"{utilities.FLAVOR.get('primary_option')} My Creator", value = f"{display_creator}", inline = True)\
        .add_field(name = info_action_name, value = info_action_value, inline = False)\
        .add_field(name = info_fun_name, value = info_fun_value, inline = False)\
        .add_field(name = info_info_name, value = info_info_value, inline = False)\
        .add_field(name = info_music_name, value = info_music_value, inline = False)\
        .add_field(name = info_feedback_name, value = info_feedback_value, inline = False)\
        .set_footer(text = f"Current Uptime: {uptime_days} days, {uptime_hours} hours, {uptime_minutes} minutes, {uptime_seconds} seconds. Thanks for having me! ❤️", icon = member.avatar_url)
        .set_author(name = "More About Aru", icon = ctx.get_guild().icon_url)\
    )

@get_info.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option('command_name','Which command would you like to learn more about?')
@lightbulb.command('command', 'Learn more about a specific command!')
@lightbulb.implements(lightbulb.SlashSubCommand, lightbulb.PrefixCommand)
async def command_info(ctx):
    if ctx.options.command_name == "addgif":
        await ctx.respond(f"{utilities.FLAVOR.get('primary_option')} Usage: `/addgif [action name] [gif_link_1, gif_link_2, ..., gif_link_10]`\
                           \n{utilities.FLAVOR.get('secondary_option')} This command allows you to add your own GIF link(s) for a specific `/action` command.\
                           \n{utilities.FLAVOR.get('secondary_option')} If a GIF is successfully added, it has a chance to show up when a user calls the respective action command.\
                           \n{utilities.FLAVOR.get('secondary_option')} Sample Usage: `/addgif bonk https://tenor.com/view/bonk-gif-21852548 https://c.tenor.com/9Q95PaJTxSYAAAAd/ina-bonk.gif`", flags = hikari.MessageFlag.EPHEMERAL)

    else:
        await ctx.respond(f"No command information found for `{ctx.options.command_name}`. (Coming soon!)")

@plugin.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option('feedback',"Your feedback here!")
@lightbulb.command('feedback', 'Got a question, comment, or suggestion? Share it with this command!')
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def feedback(ctx):
    await ctx.respond("Coming reaaaaal soon. Sorry about that! For now, address all complaints directly to my creator, Cookie, by pinging him >:)")

def load(bot):
    bot.add_plugin(plugin)
    global start_time
    start_time = datetime.datetime.now() # calculate start time of the bot