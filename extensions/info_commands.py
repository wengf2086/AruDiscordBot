import hikari
import lightbulb
import datetime
from bot import servers
import helper_functions

plugin = lightbulb.Plugin('info_commands')
start_time = None

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
    if isinstance(ctx.options.user, hikari.Member): # if the user is a Member
        member = ctx.options.user

        # get member's visible status
        if member.get_presence() == None:
            visible_status_string = "Offline"
            visible_status_emoji = "<:status_offline:1011173790354505798>"
        elif member.get_presence().visible_status == "dnd":
            visible_status_string = "Do Not Disturb"
            visible_status_emoji = "<:status_dnd:1011173792187416626>"
        else:
            visible_status_string = member.get_presence().visible_status.capitalize()
            if member.get_presence().visible_status == "online":
                visible_status_emoji = "<:status_online:1011173788311883796>"
            elif member.get_presence().visible_status == "idle":
                visible_status_emoji = "<:status_idle:1011175514251206656>"

        # get member's client status
        client_status_string = ""
        if member.get_presence() and member.get_presence().client_status.desktop == "offline": # if the user is online but not on Desktop
            if member.get_presence().client_status.mobile != "offline":
                client_status_string = "(Mobile)"
                if member.get_presence().visible_status == "online":
                    visible_status_emoji = "<:status_mobile:1011173789456936980>"

            elif member.get_presence().client_status.web != "offline":
                client_status_string = "(Web)"
                
        # get member's roles and create string of role mentions
        member_roles = await member.fetch_roles()
        # roles_mentions = f"{' '.join([role.mention if role.name is not "@everyone" for role in member_roles])}"
        roles_mentions = f"{''.join([role.mention for role in member_roles if role.name != '@everyone'])}"

        server_name = f"'{await plugin.app.rest.fetch_guild(member.guild_id)}'"
        # create embed to display information
        await ctx.respond(hikari.Embed(title = f"Member Information for {member.username}#{member.discriminator}", color = hikari.Color(0xc38ed5))\
            .set_thumbnail(member.avatar_url)\
            .add_field(name = "User", value = f"{member.mention}", inline = True)\
            .add_field(name = "User ID", value = member.id, inline = True)\
            .add_field(name = "Account Created On", value = member.created_at.strftime("%m/%d/%Y, %H:%M:%S"), inline = True)\
            .add_field(name = f"Status {visible_status_emoji}", value = f"{visible_status_string} {client_status_string}", inline = True)\
            .add_field(name = "Server Boosting Since", value = member.premium_since if member.premium_since else "Not server boosting", inline = True)\
            .add_field(name = f"Joined {server_name if len(server_name) <= 16 else 'Server'} On", value = member.joined_at.strftime("%m/%d/%Y, %H:%M:%S"), inline = True)\
            .add_field(name = f"Roles ({len(member_roles) - 1})", value = roles_mentions, inline = False)) # Does not include @everyone role

    elif isinstance(ctx.options.user, hikari.User): # if the user is a User
        user = ctx.options.user

        await ctx.respond(hikari.Embed(title = f"User Information for {user.username}#{user.discriminator}", color = hikari.Color(0xc38ed5))\
            .set_thumbnail(user.avatar_url)\
            .set_footer("This user is not a member of this server.")\
            .add_field(name = "User", value = f"{user.mention}", inline = False)\
            .add_field(name = "User ID", value = user.id, inline = False))\
            .add_field(name = "Account Created On", value = user.created_at.strftime("%m/%d/%Y, %H:%M:%S"), inline = False)

@get_info.child
@lightbulb.command('server', 'Get info on this server.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get_info_on_server(ctx):
    server = ctx.get_guild()

    bot_count, human_count, voice_count, text_count = 0, 0, 0, 0
    for i in range(0, len(server.get_members())):
        member = server.get_members().get_item_at(i)
        if not member.is_bot and not member.is_system:
            human_count += 1
        elif member.is_bot:
            bot_count += 1
    
    for i in range(0, len(server.get_channels())):
        channel = server.get_channels().get_item_at(i)
        if isinstance(channel, hikari.GuildVoiceChannel):
            voice_count += 1
        elif isinstance(channel, hikari.GuildTextChannel): 
            text_count += 1

    await ctx.respond(hikari.Embed(title = f"Server Information for {server.name}", description = server.description, color = hikari.Color(0xc38ed5))\
            .set_thumbnail(server.icon_url)\
            .add_field(name = "Server Owner", value = (await server.fetch_owner()).mention, inline = True)\
            .add_field(name = "Server ID", value = server.id, inline = True)\
            .add_field(name = "Server Created On", value = server.created_at.strftime("%m/%d/%Y, %H:%M:%S"), inline = True)\
            .add_field(name = "Member Count", value = f"{server.member_count} ({human_count} user{'s' if human_count > 1 else ''}, {bot_count} bot{'s' if bot_count > 1 else ''})", inline = True)\
            .add_field(name = "Role Count", value = f"{len(server.get_roles()) - 1}", inline = True)\
            .add_field(name = "Channel Count", value = f"{len(server.get_channels())} ({text_count} text, {voice_count} voice)", inline = True)\
            .add_field(name = "Server Boost Level", value = "No Boosts" if not server.premium_tier else server.premium_tier + "(" + str(server.premium_subscription_count) + " Boosts)", inline = False))

@get_info.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option('user', 'Mention the user you want the profile picture of or input their user ID', type = hikari.User, required = False)
@lightbulb.command('pfp', 'Get a user\'s profile picture.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get_profile_picture(ctx):
    target = ctx.author
    title = "Your Profile Picture"

    if ctx.options.user:
        target = ctx.options.user
        title = f"{target.username}'s Profile Picture"

    print(target.id)
    add_text = "Wait, that's me! Heehee!" if target.id == 1009180210823970956 else '' # If target is Aru lol
    await ctx.respond(hikari.Embed(title = title, url = str(target.display_avatar_url), color = hikari.Color(0xc38ed5)).set_image(target.display_avatar_url)\
        .set_footer(icon = plugin.app.get_me().avatar_url, text = f"What a cutie! {add_text}"))

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
    pretext += "Nice to meet you! <a:kirbywave:1009554864285683824>"
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
    action_names_string = f"{' '.join(['`' + action_name + '`' for action_name in helper_functions.get_all_action_names()])}"
    info_action_name = "<:kirbyexclamation:1011482105655595090> /action commands:"
    info_action_value = f"Get a random anime GIF of a specific action and direct it towards another user!\
                          \n{action_names_string}\
                          \n\nDid you know you can add your own GIFs? Find out how:\
                          \n`/info command addgif`"

    # Channel Management Commands Info
    info_channel_management_name = "<:kirbyblush:1011481544017318019> /channel commands (Admin Only):"
    info_channel_management_value = "Manage users in voice channels!\
                                    \n`WIP!!`"

    # Fun Commands Info
    info_fun_name = "<:kirbytongue:1011481549637697627> /fun commands:"
    info_fun_value = "Miscellaneous commands that do random fun things!"
    info_fun_value += "\n`reactbomb`: Adds multiple (max: 20) emojis to a message."
    info_fun_value += "\n\n`8ball`: Ask the Magic 8-Ball™ a yes/no question!"
    
    # Info Commands... Info
    info_info_name = "<:kirbyquestion:1011482109229158500> /info commands:"
    info_info_value = "Get info about a user, this server, me, or a specific command!\
                       \n`user` `server` `pfp` `help` `commands`"

    # Music Commands Info
    info_music_name = "<a:kirbeats:1009554827098988574> /music commands:"
    info_music_value = "Play music!\
                        \n`Also WIP!!`"

    # Suggestion Info
    
    # create embed to display information
    await ctx.respond(hikari.Embed(title = f"<a:kirbyhi:1009554846967414874> About Me", description = description, color = hikari.Color(0xc38ed5))\
        .set_thumbnail(member.avatar_url)\
        .add_field(name = f"<a:pinkheart:1012788247556018319> Joined {server_name if len(server_name) <= 16 else 'Server'} On", value = str(member.joined_at)[:19], inline = True)\
        .add_field(name = "<a:pinkheart:1012788247556018319> Total Server Count", value = f"Currently in {len(servers)} servers", inline = True)\
        .add_field(name = "<a:pinkheart:1012788247556018319> My Birthday", value = str(member.created_at)[:19], inline = False)\
        .add_field(name = "<a:pinkheart:1012788247556018319> My Creator", value = f"{display_creator}", inline = True)\
        .add_field(name = "<a:pinkheart:1012788247556018319> My User ID", value = member.id, inline = True)\
        .add_field(name = info_action_name, value = info_action_value, inline = False)\
        .add_field(name = info_channel_management_name, value = info_channel_management_value, inline = False)\
        .add_field(name = info_fun_name, value = info_fun_value, inline = False)\
        .add_field(name = info_info_name, value = info_info_value, inline = False)\
        .add_field(name = info_music_name, value = info_music_value, inline = False)\
        .add_field(name = "<:kirbylightbulb:1011482108147011593> Got a question, comment, or suggestion?", value = "Let your heart out with the `/feedback` command. I'll listen to whatever you have to say... ", inline = False)\
        .set_footer(text = f"Current Uptime: {uptime_days} days, {uptime_hours} hours, {uptime_minutes} minutes, {uptime_seconds} seconds. Thanks for having me! ❤️", icon = member.avatar_url)
        .set_author(name = "So you want to get to know me better, huh?", icon = ctx.get_guild().icon_url)\
    )

@get_info.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option('command_name','Which command would you like to learn more about?')
@lightbulb.command('command', 'Learn more about a specific command! (Supported commands: \'addgif\', \'reactbomb\')')
@lightbulb.implements(lightbulb.SlashSubCommand, lightbulb.PrefixCommand)
async def aru_info(ctx):
    # await ctx.respond("This command is in the works. Sorry about that!! <:kirbyblush:1011481544017318019>")
    if ctx.options.command_name == "addgif":
        await ctx.respond("<a:rightarrow:1012784974899990571> Usage: `/action addgif [action name] [gif_link_1, gif_link_2, ..., gif_link_10]`\
                           \n<a:purpleheart:1012784670687100999> This command allows you to add your own GIF link(s) for a specific `/action` command.\
                           \n<a:purpleheart:1012784670687100999> If a GIF is successfully added, it has a chance to show up when a user calls the respective action command.\
                           \n<a:purpleheart:1012784670687100999> Sample Usage: `/action addgif bonk https://tenor.com/view/bonk-gif-21852548 https://c.tenor.com/9Q95PaJTxSYAAAAd/ina-bonk.gif`", flags = hikari.MessageFlag.EPHEMERAL)

    elif ctx.options.command_name == "reactbomb":
        await ctx.respond("<a:rightarrow:1012784974899990571> Usage: `/fun reactbomb [emojis or preset name] [message_id (optional)]`\
                           \n<a:purpleheart:1012784670687100999> This command reacts with the specified emojis to a specific message, or the most recent message if no message is specified.\
                           \n<a:purpleheart:1012784670687100999> You can specify up to 20 emojis in the [emojis or preset name] parameter. These emojis must be available in the server you are calling the command in.\
                           \n<a:purpleheart:1012784670687100999> You can also specify a preset name instead of emojis. This will react with 20 random custom emojis from the preset.\
                           \n<a:purpleheart:1012784670687100999> Currently available presets: \"kirby\", \"sparkles\". To be added: \"jam\", \"pog\". Suggest your own preset with `/feedback`!\
                           \n<a:purpleheart:1012784670687100999> Sample Usage: `/fun reactbomb :kirbyhappy: :kirbysit:`", flags = hikari.MessageFlag.EPHEMERAL)

@plugin.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option('feedback',"Your feedback here!")
@lightbulb.command('feedback', 'Got a question, comment, or suggestion? Share it with this command!')
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def feedback(ctx):
    f = open(helper_functions.log_file_name, 'a')
    new_line = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '|' + str(ctx.author.id) + '|' + "FEEDBACK" + '|' + ctx.options.feedback + '\n'
    f.write(new_line)
    f.close()
    await ctx.respond(response_type = 4, content = f"Your comment: `{ctx.options.feedback}`\
                                                     \nThank you for helping Aru become a better bot! Your feedback is much appreciated and will be taken into consideration. <:kirbyheart:1011481547133702214>", flags = hikari.MessageFlag.EPHEMERAL)
def load(bot):
    bot.add_plugin(plugin)
    global start_time
    start_time = datetime.datetime.now()