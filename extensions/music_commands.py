from enum import unique
import lightbulb
import hikari
import lavaplayer
import logging
import asyncio
import uuid
import math

plugin = lightbulb.Plugin('music_commands')

lavalink = lavaplayer.Lavalink( # Lavalink object
    host="78.108.218.93",
    port=25538,
    password="mysparkedserver",
    user_id=173555466176036864
)

is_paused = False

@plugin.listener(hikari.StartedEvent) # Connect Lavalink when Bot Starts
async def on_start(event: hikari.StartedEvent):
    lavalink.set_user_id(plugin.app.get_me().id)
    lavalink.set_event_loop(asyncio.get_event_loop())
    lavalink.connect()
@plugin.listener(hikari.VoiceStateUpdateEvent) # Update Lavalink node on voice state update
async def voice_state_update(event):
    await lavalink.raw_voice_state_update(event.guild_id, event.state.user_id, event.state.session_id, event.state.channel_id)
@plugin.listener(hikari.VoiceServerUpdateEvent) # Update Lavalink node when on voice server update
async def voice_server_update(event):
    await lavalink.raw_voice_server_update(event.guild_id, event.endpoint, event.token)

# Auxiliary Functions

#Converts milliseconds to a string containing hours, minutes, seconds
def convert_milliseconds(ms):
    seconds = str((ms//1000)%60)
    minutes = str((ms//(1000*60))%60)
    hours = str((ms//(1000*60*60)))
    if float(hours) >= 1:
        return f"{hours.zfill(2)}:{minutes.zfill(2)}:{seconds.zfill(2)}"
    else:
        return f"{minutes.zfill(2)}:{seconds.zfill(2)}"

#Converts a string of time in hh:mm:ss: format to milliseconds
def convert_to_milliseconds(hms):
    time = hms.split(":")
    hours = (int)(time[0])
    minutes = (int)(time[1])
    seconds = (int)(time[2])
    return hours * 3600000 + minutes * 60000 + seconds * 1000

def get_total_length_of_tracks(tracklist):
    sum_in_milliseconds = 0
    for track in tracklist:
        sum_in_milliseconds += track.length
    return convert_milliseconds(sum_in_milliseconds)

# Commands
@plugin.command 
@lightbulb.command('music', 'Play music!')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def music(ctx):
    pass

async def try_join(ctx, states):
    if not states:
        return 0
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]
    if not voice_state:
        return 0
    channel_id = voice_state[0].channel_id
    await plugin.app.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    await lavalink.wait_for_connection(ctx.guild_id)
    return channel_id

@music.child
@lightbulb.command("join", "Join your voice channel.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def join(ctx):
    states = plugin.app.cache.get_voice_states_view_for_guild(ctx.guild_id)
    channel_id = await try_join(ctx, states)
    if not channel_id:
        await ctx.respond("You are not in a voice channel. Join one first!")
        return
    await ctx.respond(f"Joined <#{channel_id}>!")

@music.child
@lightbulb.option("query", "Search for a song or input a YouTube link!")
@lightbulb.command("play", "Play a song or playlist!", aliases=["p"], auto_defer = True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def play(ctx):
    # If the bot is not in a voice channel, attempt to join one
    states = plugin.app.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == plugin.app.get_me().id)]
    if not voice_state: 
        channel_id = await try_join(ctx, states)
        if not channel_id:
            await ctx.respond("You are not in a voice channel. Join one first!")
            return
        else:
            await ctx.respond(f"Joined <#{channel_id}>!")

    # Parse Query
    query = ctx.options.query
    result = await lavalink.auto_search_tracks(ctx.options.query)  # Search the query
    if not result:
        await ctx.respond("No result found for the specified query. Please try again.")
        return
    elif isinstance(result, lavaplayer.TrackLoadFailed):  # if track fails to load
        await ctx.respond("Track load failed, try again later.\n```{}```".format(result.message))
        return
    
    number_emojis = { # emojis for numbering the query results
        1 : "<a:num_1:1013543442242097263>",
        2: "<a:num_2:1013543441113829487>",
        3: "<a:num_3:1013543439499022476>",
        4: "<a:num_4:1013543437934534656>",
        5: "<a:num_5:1013543436726566972>"
    }

    if isinstance(result, list) and len(result) > 1: # A query, not a URL. Show query and allow user to select an option.
        unique_id = uuid.uuid1() # 36 character unique identifier to receive unique interaction responses
        display_query = ""
        buttons = plugin.app.rest.build_action_row()
        display_len = 5 if len(result) >= 5 else len(result)
        for i in range(display_len): # [{i.title}]({i.uri})
            display_query += f"<a:pinkheart:1012788247556018319>{number_emojis.get(i+1)} [{result[i].title}]({result[i].uri}) ({convert_milliseconds(result[i].length)})\n\n"
            buttons.add_button(2, f"qs|{i}|{unique_id}").set_emoji(hikari.Emoji.parse(number_emojis.get(i+1))).add_to_container()
        
        embed = hikari.Embed(title = f"Select a song to add to the queue!", description = display_query, color = hikari.Color(0xc38ed5))\
        .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
        .set_author(name = f"Query Results For: \"{query}\"", icon = plugin.app.get_me().avatar_url)
        
        initial_response = await ctx.respond(embed = embed, component = buttons)
        query_selection = await respond_to_interaction(15, str(unique_id))
        if query_selection == -1: # Response time-out
            await plugin.app.rest.edit_message(channel = ctx.channel_id, message = await initial_response.message(), content = "No song was selected. The query has been cancelled.", embed = None, component = None)
            return
        else:
            await lavalink.play(ctx.guild_id, result[query_selection], ctx.author.id)
            embed = hikari.Embed(title = f"Song Selected:", \
                                 description = f"<a:pinkheart:1012788247556018319>{number_emojis.get(query_selection+1)} [{result[query_selection].title}]({result[query_selection].uri}) ({convert_milliseconds(result[query_selection].length)})", \
                                 color = hikari.Color(0xc38ed5)) \
            .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
            .set_author(name = f"The following song has been added to the queue.", icon = plugin.app.get_me().avatar_url)
            await plugin.app.rest.edit_message(channel = ctx.channel_id, message = await initial_response.message(), content = f"A song has been selected.", embed = embed, component = None)
        return

    else: # A URL
        if "&list=" in query:
            unique_id = uuid.uuid1() # 36 character unique identifier to receive unique interaction responses
            playlist_url = f"https://www.youtube.com/playlist?{query[query.index('list='):]}"
            single_url = query[:query.index('&list=')]
            result = await lavalink.auto_search_tracks(single_url)
            requested_song = f"<a:pinkheart:1012788247556018319> [{result[0].title}]({result[0].uri}) ({convert_milliseconds(result[0].length)})"
            buttons = plugin.app.rest.build_action_row()
            buttons.add_button(3, f"pl|1|{unique_id}").set_label("Yes").add_to_container()
            buttons.add_button(4, f"pl|0|{unique_id}").set_label("No").add_to_container()

            embed = hikari.Embed(title = f"Song Requested", description = f"{requested_song}\n\n**The requested song belongs to a playlist. Do you want to add the whole playlist as well?**", color = hikari.Color(0xc38ed5))\
            .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
            .set_author(name = f"The followign song has been requested.", icon = plugin.app.get_me().avatar_url)

            initial_response = await ctx.respond(embed = embed, component = buttons)

            playlist_selection = await respond_to_interaction(15, str(unique_id))
            if playlist_selection == 1: # If "Yes" was selected
                result = await lavalink.auto_search_tracks(playlist_url)
                await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
                embed = hikari.Embed(title = f"Playlist added: ", \
                                    description = f"<a:pinkheart:1012788247556018319> [{result.name}]({playlist_url}) ({get_total_length_of_tracks(result.tracks)}), {len(result.tracks)} songs total", \
                                    color = hikari.Color(0xc38ed5)) \
                .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
                .set_author(name = f"Multiple songs have been added to the queue.", icon = plugin.app.get_me().avatar_url)

                await plugin.app.rest.edit_message(channel = ctx.channel_id, message = await initial_response.message(), content = "Playlist added!", embed = embed, component = None)
                return
            else: # If "No" was selected, or the interaction times out
                result = await lavalink.auto_search_tracks(single_url)
                await lavalink.play(ctx.guild_id, result[0], ctx.author.id)
                embed = hikari.Embed(title = f"Song requested", description = f"{requested_song}\n\n**The corresponding playlist was not added.**", color = hikari.Color(0xc38ed5))\
                .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
                .set_author(name = f"The following song has been added to the queue.", icon = plugin.app.get_me().avatar_url)
                await plugin.app.rest.edit_message(channel = ctx.channel_id, message = await initial_response.message(), content = "Playlist was not added.", embed = embed, component = None)
                return
    
        if isinstance(result, lavaplayer.PlayList):
            await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)

            embed = hikari.Embed(title = f"Playlist added: ", \
                                 description = f"<a:pinkheart:1012788247556018319> [{result.name}]({query}) ({get_total_length_of_tracks(result.tracks)}), {len(result.tracks)} songs total", \
                                 color = hikari.Color(0xc38ed5)) \
            .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
            .set_author(name = f"Multiple songs have been added to the queue.", icon = plugin.app.get_me().avatar_url)
            await ctx.respond(embed = embed)
            return 
        else:
            await lavalink.play(ctx.guild_id, result[0], ctx.author.id)
            embed = hikari.Embed(title = f"Song requested:", \
                                 description = f"<a:pinkheart:1012788247556018319> [{result[0].title}]({result[0].uri}) ({convert_milliseconds(result[0].length)})", \
                                 color = hikari.Color(0xc38ed5)) \
            .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
            .set_author(name = f"The following song has been added to the queue.", icon = plugin.app.get_me().avatar_url)
            await ctx.respond(embed = embed)
            return

async def respond_to_interaction(time_out, unique_id):
    try:
        event = await plugin.bot.wait_for(hikari.InteractionCreateEvent, time_out, (lambda event: event.interaction.type == 3 and event.interaction.custom_id.split("|")[2] == unique_id))
    
    except:
        return -1

    custom_id = event.interaction.custom_id.split("|")
    if(custom_id[0] == "qs"):
        return int(custom_id[1]) # Return 0, 1, 2, 3, or 4

    elif(custom_id[0] == "pl"):
        return int(custom_id[1]) # Return 0 or 1
    
    elif(custom_id[0] == "page"):
        return int(custom_id[1]) # Return page number corresponding to button

@music.child
@lightbulb.command("pause", "Pause the current song!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def pause(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("No song is playing!")
        return
    
    global is_paused
    if is_paused:
        await ctx.respond("The song is already paused!")
        return

    await lavalink.pause(ctx.guild_id, True)
    
    is_paused = True
    await ctx.respond("Music paused!")

@music.child
@lightbulb.command("resume", "Resume playing the current song!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def resume(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("There is no song to resume!")
        return

    global is_paused
    if not is_paused:
        await ctx.respond("The song is already playing!")
        return

    is_paused = False
    await lavalink.pause(ctx.guild_id, False)
    await ctx.respond("Music resumed!")

@music.child
@lightbulb.command("stop", "Stop the player and clear the queue!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def stop(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("The queue is already empty!")
        return
    
    await lavalink.stop(ctx.guild_id)
    await ctx.respond("Stopped the player and cleared the queue.")

@music.child
@lightbulb.command("skip", "Skip the current song!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def skip(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("The queue is already empty!")
        return
    await lavalink.skip(ctx.guild_id)
    await ctx.respond("Skipped the current song.")

@music.child
@lightbulb.option("position", "Position to seek (Format: mm:ss or hh:mm:ss)")
@lightbulb.command("seek", "Seek a position in the song!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def seek(ctx): # Convert input to milliseconds
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("Nothing is playing right now!")
        return

    time = ctx.options.position.split(":")
    if not (len(time) == 2 or len(time) == 3):
        await ctx.respond(f"Invalid position {ctx.options.position}. Please make sure that the position is in the following format: `mm:ss` or `hh:mm:ss`.")
        return
    
    position = ctx.options.position
    if len(time) == 2: # if mm:ss, pad with '00:'
        position = "00:" + ctx.options.position
    
    ms = convert_to_milliseconds(position)
        
    await lavalink.seek(ctx.guild_id, ms)
    await ctx.respond(f"Position `{ctx.options.position}` seeked!")

@music.child
@lightbulb.command("queue", "Display the current queue", auto_defer = True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def queue(ctx):
    # Check node and queue and return if either are None
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("The queue is empty!")
        return

    queue = node.queue
    queue_len = len(queue) # number of tracks in the queue
    page_len = 10 # tracks to display per page
    num_pages = int(math.ceil(queue_len / page_len)) # total number of pages
    display_queue = [] # list containing strings for each track

    # build the display queue
    for i in range(0,queue_len):
        # requester = await plugin.app.rest.fetch_member(guild = ctx.guild_id, user = queue[i].requester)
        # String to be displayed in the queue for this song
        song_display = f"**[{i+1}]** [{queue[i].title}]({queue[i].uri}) ({convert_milliseconds(queue[i].length)})"
        if i == 0: # first song has a different emoji
            song_display = "<a:pinkheart:1012788247556018319> " + song_display + "\n_(currently playing)_\n"
        else:
            song_display = "<a:purpleheart:1012784670687100999>" + song_display + "\n"

        display_queue.append(song_display)
    
    unique_id = "lol" # 36 character unique identifier to receive unique interaction responses for this Queue
    # method to assemble the current page
    def assemble_page(current_page):
        first_page_entry = current_page * 10
        last_page_entry = (current_page * 10 + 9) if (current_page * 10 + 9) < queue_len else queue_len
        page_display = "\n".join(display_queue[first_page_entry:last_page_entry])

        # create embed
        embed = hikari.Embed(title = f"<a:kirbydance:1009554839602204712> Current Queue ({len(queue)} songs, {get_total_length_of_tracks(queue)} total length)", description = f"{page_display}", color = hikari.Color(0xc38ed5))\
        .set_footer(f"Page [{current_page + 1}/{num_pages}] | loop mode: {'ON' if node.repeat == True else 'OFF'} | loopqueue mode: {'ON' if node.queue_repeat == True else 'OFF'} | Thank you for using Aru.")

        # assemble Previous and Next Page Buttons
        prev_button_to_page = current_page - 1
        next_button_to_page = current_page + 1

        buttons = plugin.app.rest.build_action_row() 
        if not (prev_button_to_page < 0): # check if index out of bounds. if yes, disable the button
            buttons.add_button(2, f"page|{prev_button_to_page}|{unique_id}").set_emoji(hikari.Emoji.parse("<:frogarrowleft:1013685036362502186>")).add_to_container()
        else:
            buttons.add_button(2, f"invalid|{prev_button_to_page}|{unique_id}").set_emoji(hikari.Emoji.parse("<:frogarrowleft:1013685036362502186>")).set_is_disabled(True).add_to_container()
        
        if not (next_button_to_page >= num_pages): # check if index out of bounds. if yes, disable the button
            buttons.add_button(2, f"page|{next_button_to_page}|{unique_id}").set_emoji(hikari.Emoji.parse("<:frogarrowright:1013683523317673994>")).add_to_container()
        else: 
            buttons.add_button(2, f"invalid|{next_button_to_page}|{unique_id}").set_emoji(hikari.Emoji.parse("<:frogarrowleft:1013685036362502186>")).set_is_disabled(True).add_to_container()

        return embed, buttons
    
    # Start with first page
    current_page = 0
    embed, buttons = assemble_page(current_page)
    response = await ctx.respond(embed=embed, component=buttons)
    
    while (new_page := (await respond_to_interaction(15, unique_id))) != -1:
        new_embed, new_buttons = assemble_page(new_page)
        await plugin.app.rest.edit_message(channel = ctx.channel_id, message = await response.message(), content = f"", embed = new_embed, component = new_buttons)

@music.child
@lightbulb.option("position", "The queue position of the song you wish to remove.")
@lightbulb.command("remove", "Remove a song from the queue.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def remove(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("The queue is empty!")
        return
    await ctx.respond("WIP lol")

@music.child
@lightbulb.command("np", "Check what song is currently playing.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def np_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("Nothing is playing right now!")
        return
    await ctx.respond(f"[{node.queue[0].title}]({node.queue[0].uri})")

@music.child
@lightbulb.command("loop", "Toggle loop mode on/off", aliases=["l", "repeat"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def loop_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("Nothing is playing right now!")
        return
    stats = False if node.repeat else True
    await lavalink.repeat(ctx.guild_id, stats)

    if stats:
        await ctx.respond("Now looping this song.")
        return
    await ctx.respond("Stopped looping this song.")

@music.child
@lightbulb.command("loopqueue", "Toggle loop queue mode on/off.", aliases=["lq", "repeat_queue", "repeat_q"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def loop_queue_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("The queue is empty!")
        return
    stats = False if node.queue_repeat else True
    await lavalink.queue_repeat(ctx.guild_id, stats)

    if stats:
        await ctx.respond("Now looping the queue.")
        return
    await ctx.respond("Stopped looping the queue.")

@music.child
@lightbulb.command("shuffle", "Shuffle the queue!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def shuffle_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("The queue is empty!")
        return
    await lavalink.shuffle(ctx.guild_id)
    await ctx.respond("Shuffled the music!")

@music.child
@lightbulb.command("leave", "Leave the voice channel.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def leave_command(ctx):
    states = plugin.app.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == plugin.app.get_me().id)]
    if not voice_state: 
        await ctx.respond(f"I'm not in a voice channel!")
        return
    
    await plugin.app.update_voice_state(ctx.guild_id, None)
    await ctx.respond("Okay, okay, I'm leaving! >:(")

# logging
@lavalink.listen(lavaplayer.TrackStartEvent)
async def track_start_event(event: lavaplayer.TrackStartEvent):
    logging.info(f"start track: {event.track.title}")
@lavalink.listen(lavaplayer.TrackEndEvent)
async def track_end_event(event: lavaplayer.TrackEndEvent):
    logging.info(f"track end: {event.track.title}")
@lavalink.listen(lavaplayer.WebSocketClosedEvent)
async def web_socket_closed_event(event: lavaplayer.WebSocketClosedEvent):
    logging.error(f"error with websocket {event.reason}")

def load(bot):
    bot.add_plugin(plugin)
    lavalink.connect()