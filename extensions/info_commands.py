import hikari
import lightbulb
import datetime

plugin = lightbulb.Plugin('info_commands')

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
        elif member.get_presence().visible_status == "dnd":
            visible_status_string = "Do Not Disturb"
        else:
            visible_status_string = member.get_presence().visible_status.capitalize()
    
        # get member's client status
        client_status_string = ""
        if member.get_presence() and member.get_presence().client_status.desktop == "offline": # if the user is online but not on Desktop
            if member.get_presence().client_status.mobile != "offline":
                client_status_string = "(Mobile)"
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
            .add_field(name = "Status", value = f"{visible_status_string} {client_status_string}", inline = True)\
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
    await ctx.respond(hikari.Embed(title = title, url = str(target.display_avatar_url), color = hikari.Color(0xc38ed5)).set_image(target.display_avatar_url)\
        .set_footer(icon = plugin.app.get_me().avatar_url, text = "What a cutie!"))

@get_info.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.command('help', 'Learn more about me, Aru! :3c')
@lightbulb.implements(lightbulb.SlashSubCommand, lightbulb.PrefixCommand)
async def aru_info(ctx):
    member = ctx.get_guild().get_member(plugin.app.get_me().id)

    server_name = f"'{await plugin.app.rest.fetch_guild(member.guild_id)}'"

    pretext = f"Hi, I'm {member.mention}. "
    if member.display_name != member.username:
        pretext += "Wait, did someone change my name...? Anyways, my _real_ name is Aru. "
    pretext += "Nice to meet you! :3c"
    description = pretext + ""
    # create embed to display information
    await ctx.respond(hikari.Embed(title = f"About Me", description = description, color = hikari.Color(0xc38ed5))\
        .set_thumbnail(member.avatar_url)\
        .add_field(name = "My User ID", value = member.id, inline = True)\
        .add_field(name = "My Birthday", value = str(member.created_at)[:19], inline = True)\
        .add_field(name = f"Joined {server_name if len(server_name) <= 16 else 'Server'} On", value = str(member.joined_at)[:19], inline = True)\
        .add_field(name = "Current Uptime", value = "None"))

def load(bot):
    bot.add_plugin(plugin)