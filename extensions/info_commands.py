import hikari
import lightbulb

plugin = lightbulb.Plugin('info_commands')

@plugin.command 
@lightbulb.command('info', 'Get info on a user or server.')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def get_info(ctx):
    pass

@get_info.child
@lightbulb.option('user', 'Mention the user you want to inspect or input their name#tag or user ID.')
@lightbulb.command('user', 'Get info on a user.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get_info_on_user(ctx):
    user_id = 0
    if ctx.options.user.startswith("<") and ctx.options.user.endswith(">"): # if input is a Mention
        user_id = int(ctx.options.user[3:-1])
        print("beep")
    else: # input is a raw user ID
        user_id = int(ctx.options.user)
        print("boop")
        
    embed = None
    
    try:
        member = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = user_id) # if user is a Guild Member, show member info
        print("MEMBER")
        embed = hikari.Embed(title = f"Member Information for {member.username}#{member.discriminator}", color = hikari.Color(0xc38ed5))\
            .set_thumbnail(member.avatar_url)\
            .add_field(name = "User", value = f"{member.mention}", inline = True)\
            .add_field(name = "Account Created On", value = str(member.created_at)[:19], inline = True)\
            .add_field(name = "User ID", value = member.id, inline = True)\
            .add_field(name = "Status", value = "do not disturb" if member.get_presence().visible_status == "dnd" else member.get_presence().visible_status, inline = True)\
            .add_field(name = f"Joined '{await plugin.app.rest.fetch_guild(member.guild_id)}' On", value = str(member.joined_at)[:19], inline = True)\
            .add_field(name = "Server Boosting Since", value = member.premium_since if member.premium_since else "Not server boosting", inline = True)\
            .add_field(name = "Roles", value = "temp", inline = False)
        await ctx.respond(embed = embed)
        return

    except:
        print("NOT A MEMBER")

    try:
        user = await plugin.app.rest.fetch_user(user = user_id) # Otherwise show user info
        print("USER")
        embed = hikari.Embed(title = f"User Information for {user.username}#{user.discriminator}", color = hikari.Color(0xc38ed5))\
            .set_thumbnail(user.avatar_url)\
            .set_footer("This user is not a member of this server.")\
            .add_field(name = "User", value = f"{user.mention}", inline = False)\
            .add_field(name = "Account Created On", value = str(user.created_at)[:19], inline = False)\
            .add_field(name = "User ID", value = user.id, inline = False)
        await ctx.respond(embed = embed)
        return
    except:
        print("NOT A USER")

    return
    
    # User does not exist
    # return here

    # cookie#0867
    # Server Join Date
    # User ID = ctx.options.user.id
    # Status
    # Profile Picture and link to PFP

# @get_info.child
# @lightbulb.option('server', 'Input the server ID of the server you want to inspect.', type = hikari.Guild)
# @lightbulb.command('server', 'Get info on a server.')
# @lightbulb.implements(lightbulb.SlashSubCommand)
# async def get_info_on_server(ctx):

# @get_info.child
# @lightbulb.option('id', 'Input the user or server ID you wish to extract the profile picture from.')
# @lightbulb.command('pfp', 'Get a user or server\'s profile picture.')
# @lightbulb.implements(lightbulb.SlashSubCommand)
# async def get_profile_picture(ctx):


def load(bot):
    bot.add_plugin(plugin)