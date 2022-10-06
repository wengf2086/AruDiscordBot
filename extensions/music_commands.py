from enum import unique
import lightbulb
import hikari
import lavaplayer
import logging
import asyncio
import uuid
import math
import utilities

plugin = lightbulb.Plugin('music_commands')

lavalink = utilities.LAVALINK

@plugin.listener(hikari.StartedEvent) # Connect Lavalink when Bot Starts
async def on_start(event: hikari.StartedEvent):
    lavalink.set_user_id(plugin.app.get_me().id)
    lavalink.set_event_loop(asyncio.get_event_loop())
    lavalink.connect()

@plugin.listener(hikari.VoiceStateUpdateEvent) # Update Lavalink node on voice state update
async def voice_state_update(event):
    
    await lavalink.raw_voice_state_update(event.guild_id, event.state.user_id, event.state.session_id, event.state.channel_id)

    # Leave if there is no one else in the voice channel
    voice_state = plugin.app.cache.get_voice_state(event.guild_id, plugin.app.get_me())
    if(voice_state):
        voice_channel_id = voice_state.channel_id
        voice_states = plugin.app.cache.get_voice_states_view_for_channel(event.guild_id, voice_channel_id).values()
        other_users = filter(lambda user: not user.member.is_bot, voice_states) # look for users that are not bots
        num_users_in_vc = len(list(other_users))
        if(num_users_in_vc == 0):
            await plugin.app.update_voice_state(event.guild_id, None)

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

# Given a list of tracks, get the total length of the list
def get_total_length_of_tracks(tracklist):
    sum_in_milliseconds = 0
    for track in tracklist:
        sum_in_milliseconds += track.length
    return convert_milliseconds(sum_in_milliseconds)

# Commands
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

@plugin.command
@lightbulb.command("join", "[🎵] Join your voice channel.")
@lightbulb.implements(lightbulb.SlashCommand)
async def join(ctx):
    states = plugin.app.cache.get_voice_states_view_for_guild(ctx.guild_id)
    channel_id = await try_join(ctx, states)
    if not channel_id:
        await ctx.respond("You are not in a voice channel. Join one first!")
        return
    await ctx.respond(f"Joined <#{channel_id}>!")

@plugin.command
@lightbulb.option("query", "Search a song or input a link! (YouTube, Spotify, Soundcloud, Bandcamp, Twitch, and Vimeo supported)")
@lightbulb.command("play", "[🎵] Play a song or playlist!", aliases=["p"], auto_defer = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def play(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    states = plugin.app.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == plugin.app.get_me().id)]
    if not voice_state: # If the bot is not in a voice channel, attempt to join one
        channel_id = await try_join(ctx, states)
        if not channel_id:
            await ctx.respond("You are not in a voice channel. Join one first!")
            return
        else:
            await ctx.respond(f"Joined <#{channel_id}>!")

    query = ctx.options.query # parse the query

    # Spotify (uses spotilink)
    if query.startswith("https://open.spotify.com/"):
        if query.startswith("https://open.spotify.com/track/"): # Link to a single track
            await ctx.respond("This is a spotify track.")
            pass

        elif query.startswith("https://open.spotify.com/album/"): # Link to an album
            await ctx.respond("This is a spotify album.")
            pass

        elif query.startswith("https://open.spotify.com/playlist/"): # Link to a playlist
            await ctx.respond("This is a spotify playlist.")
            pass

    # YouTube, Bandcamp, Soundcloud, Twitch, Vimeo (uses lavalink)
    else:
        result = await lavalink.auto_search_tracks(ctx.options.query)  # Search the query
        if not result: # No result found, return
            await ctx.respond("No result found for the specified query. Please try again.")
            return

        elif isinstance(result, lavaplayer.TrackLoadFailed):  # Track failed to load, return
            await ctx.respond("Track load failed, try again later.\n```{}```".format(result.message))
            return

        # result is a query. Show the query and allow the user to select an option
        elif isinstance(result, list) and len(result) > 1: 
            unique_id = str(uuid.uuid1()) # 36 character unique identifier to receive unique interaction responses
            buttons = plugin.app.rest.build_action_row()
            display_query = ""
            display_len = 5 if len(result) >= 5 else len(result) # Number of options to show. If there are less than 5 results, just whatever there is.
            for i in range(display_len): # Display display_len options
                number_emoji = utilities.FLAVOR.get(f'num_{i+1}') # Get corresponding number emoji
                display_query += f"{utilities.FLAVOR.get('primary_option')}{number_emoji} [{result[i].title}]({result[i].uri}) ({convert_milliseconds(result[i].length)})\n\n" # The query option string
                buttons.add_button(2, f"qs|{i}|{unique_id}").set_emoji(hikari.Emoji.parse(number_emoji)).add_to_container() # Add the corresponding button
            
            # Embed for Query Selection Message
            embed = hikari.Embed(title = f"Select a song to add to the queue!", description = display_query, color = hikari.Color(0xc38ed5))\
            .set_author(name = f"Query Results For: \"{query}\"", icon = plugin.app.get_me().avatar_url)
            
            # Send the embed
            initial_response = await ctx.respond(embed = embed, component = buttons)

            # Wait for the user's selection and store it in query_selection, or time-out
            query_selection = await respond_to_interaction(15, str(unique_id), ctx.author.id)

            if query_selection == -1: # Response time-out
                embed = hikari.Embed(title = f"No song selected", \
                                    description = f"No song was selected, so nothing was added to the queue.", \
                                    color = hikari.Color(0xc38ed5)) \
                .set_author(name = f"Nothing was added to the queue.", icon = plugin.app.get_me().avatar_url)
                await plugin.app.rest.edit_message(channel = ctx.channel_id, message = await initial_response.message(), embed = embed, component = None)
                return
            else: 
                number_emoji = utilities.FLAVOR.get(f'num_{query_selection+1}') # Get corresponding number emoji

                await lavalink.play(ctx.guild_id, result[query_selection], ctx.author.id) # Add the selected track to the queue

                # Embed for Query Selected Message
                embed = hikari.Embed(title = f"Song selected:", \
                                    description = f"{utilities.FLAVOR.get('primary_option')} {number_emoji} [{result[query_selection].title}]({result[query_selection].uri}) ({convert_milliseconds(result[query_selection].length)})", \
                                    color = hikari.Color(0xc38ed5)) \
                .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
                .set_author(name = f"The following song has been added to the queue at position {len(node.queue) if node else 1}.", icon = plugin.app.get_me().avatar_url)

                # Edit the initial Query Selection Message to reflect the Query Selection
                await plugin.app.rest.edit_message(channel = ctx.channel_id, message = await initial_response.message(), embed = embed, component = None)

        # result is a URL. Check if URL is a playlist or a single track
        else:
            # URL leads to a track that is part of a playlist. Ask the user if they want to queue the whole playlist.
            if "&list=" in query:
                unique_id = uuid.uuid1() # 36 character unique identifier to receive unique interaction responses
                single_url = query[:query.index('&list=')] # get the link to the single track
                playlist_url = f"https://www.youtube.com/playlist?{query[query.index('list='):]}" # construct the link to the playlist that the track belongs to
                result = await lavalink.auto_search_tracks(single_url) # Search the individual track
                playlist_result = await lavalink.auto_search_tracks(playlist_url) # Search the playlist
                requested_song = f"{utilities.FLAVOR.get('primary_option')} [{result[0].title}]({result[0].uri}) ({convert_milliseconds(result[0].length)})"

                buttons = plugin.app.rest.build_action_row()
                buttons.add_button(3, f"pl|1|{unique_id}").set_label("Yes").add_to_container()
                buttons.add_button(4, f"pl|0|{unique_id}").set_label("No").add_to_container()
            
                # Embed for Playlist Add Selection
                embed = hikari.Embed(title = f"Song Requested", description = f"{requested_song}\n\n**The requested song belongs to a playlist:**\n\
                    {utilities.FLAVOR.get('secondary_option')} [{playlist_result.name}]({playlist_url}) ({get_total_length_of_tracks(playlist_result.tracks)}), {len(playlist_result.tracks)} songs total\n\
                    \n**Do you want to add the whole playlist as well?**", color = hikari.Color(0xc38ed5))\
                .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
                .set_author(name = f"The following song has been requested.", icon = plugin.app.get_me().avatar_url)

                # Send the Embed
                initial_response = await ctx.respond(embed = embed, component = buttons)

                # Wait for the user's selection and store it in playlist_selection
                playlist_selection = await respond_to_interaction(15, str(unique_id), ctx.author.id)

                if playlist_selection == 1: # If "Yes" was selected
                    await lavalink.add_to_queue(ctx.guild_id, playlist_result.tracks, ctx.author.id) # Add the whole playlist to the queue

                    # Embed for Playlist Added Confirmation Message
                    embed = hikari.Embed(title = f"Playlist added: ", \
                                        description = f"{utilities.FLAVOR.get('primary_option')} [{playlist_result.name}]({playlist_url}) ({get_total_length_of_tracks(playlist_result.tracks)}), {len(playlist_result.tracks)} songs total", \
                                        color = hikari.Color(0xc38ed5)) \
                    .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
                    .set_author(name = f"Multiple songs have been added to the queue.", icon = plugin.app.get_me().avatar_url)

                    # Edit the initial Playlist Add Selection message to reflect that the playlist has been added
                    await plugin.app.rest.edit_message(channel = ctx.channel_id, message = await initial_response.message(), embed = embed, component = None)
                    
                else: # If "No" was selected, or the interaction times out
                    await lavalink.play(ctx.guild_id, result[0], ctx.author.id) # Add the single track to the queue

                    # Embed for Playlist Not Added Confirmation Message
                    embed = hikari.Embed(title = f"Song requested", description = f"{requested_song}\n\n**The corresponding playlist was not added.**", color = hikari.Color(0xc38ed5))\
                    .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
                    .set_author(name = f"The following song has been added to the queue at position {len(node.queue)}.", icon = plugin.app.get_me().avatar_url)

                    # Edit the initial Playlist Add Selection message to reflect that the playlist has not been added
                    await plugin.app.rest.edit_message(channel = ctx.channel_id, message = await initial_response.message(), embed = embed, component = None)

            # URL leads to a playlist
            elif isinstance(result, lavaplayer.PlayList):
                await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id) # Add the playlist to the queue

                # Embed for Playlist Added Message
                embed = hikari.Embed(title = f"Playlist added: ", \
                                    description = f"{utilities.FLAVOR.get('primary_option')} [{result.name}]({query}) ({get_total_length_of_tracks(result.tracks)}), {len(result.tracks)} songs total", \
                                    color = hikari.Color(0xc38ed5)) \
                .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
                .set_author(name = f"Multiple songs have been added to the queue.", icon = plugin.app.get_me().avatar_url)

                # Send the Embed
                await ctx.respond(embed = embed)

            # URL leads to a track that is not part of a playlist
            else: 
                await lavalink.play(ctx.guild_id, result[0], ctx.author.id) # Add the track to the queue

                # Embed for Song Requested Message
                embed = hikari.Embed(title = f"Song requested:", \
                                    description = f"{utilities.FLAVOR.get('primary_option')} [{result[0].title}]({result[0].uri}) ({convert_milliseconds(result[0].length)})", \
                                    color = hikari.Color(0xc38ed5)) \
                .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
                .set_author(name = f"The following song has been added to the queue.", icon = plugin.app.get_me().avatar_url)

                # Send the Embed
                await ctx.respond(embed = embed)

async def respond_to_interaction(time_out, unique_id, author):
    try:
        event = await plugin.bot.wait_for(hikari.InteractionCreateEvent, time_out, (lambda event: event.interaction.user.id == author and event.interaction.type == 3 and event.interaction.custom_id.split("|")[2] == unique_id))
    except:
        return -1

    custom_id = event.interaction.custom_id.split("|")

    await event.interaction.create_initial_response(response_type = 7)
    if(custom_id[0] == "qs"):
        return int(custom_id[1]) # Return 0, 1, 2, 3, or 4

    elif(custom_id[0] == "pl"):
        return int(custom_id[1]) # Return 0 or 1
    
    elif(custom_id[0] == "page"):
        return int(custom_id[1]) # Return page number corresponding to button

@plugin.command
@lightbulb.command("pause", "[🎵] Pause the current song!")
@lightbulb.implements(lightbulb.SlashCommand)
async def pause(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("No song is playing!", flags = hikari.MessageFlag.EPHEMERAL)
        return

    if node.is_pause:
        await ctx.respond("The player is already paused!", flags = hikari.MessageFlag.EPHEMERAL)

    await lavalink.pause(ctx.guild_id, True)
    
    await ctx.respond("Music paused!")

@plugin.command
@lightbulb.command("resume", "[🎵] Resume playing the current song!")
@lightbulb.implements(lightbulb.SlashCommand)
async def resume(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("There is no song to resume!", flags = hikari.MessageFlag.EPHEMERAL)
        return

    if not node.is_pause:
        await ctx.respond("The player is already playing!", flags = hikari.MessageFlag.EPHEMERAL)

    await lavalink.pause(ctx.guild_id, False)
    await ctx.respond("Music resumed!")

@plugin.command
@lightbulb.command("stop", "[🎵] Stop the player and clear the queue!")
@lightbulb.implements(lightbulb.SlashCommand)
async def stop(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("The queue is already empty!")
        return
    
    await lavalink.stop(ctx.guild_id)
    await ctx.respond("Stopped the player and cleared the queue.")

@plugin.command
@lightbulb.command("skip", "[🎵] Skip the current song!")
@lightbulb.implements(lightbulb.SlashCommand)
async def skip(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("The queue is already empty!")
        return
    await lavalink.skip(ctx.guild_id)
    await ctx.respond("Skipped the current song.")

@plugin.command
@lightbulb.option("position", "Position to seek (Format: mm:ss or hh:mm:ss)")
@lightbulb.command("seek", "[🎵] Seek a position in the song!")
@lightbulb.implements(lightbulb.SlashCommand)
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

@plugin.command
@lightbulb.command("queue", "[🎵] Display the current queue", auto_defer = True)
@lightbulb.implements(lightbulb.SlashCommand)
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
            song_display = f"{utilities.FLAVOR.get('primary_option')} " + song_display + f" _requested by <@{queue[i].requester}>_" + "\n"
        else:
            song_display = f"{utilities.FLAVOR.get('secondary_option')} " + song_display + f" _requested by <@{queue[i].requester}>_" + "\n"

        display_queue.append(song_display)
    
    unique_id = str(uuid.uuid1()) # 36 character unique identifier to receive unique interaction responses for this Queue

    # method to assemble the current page
    def assemble_page(current_page):
        first_page_entry = current_page * 10
        last_page_entry = (current_page * 10 + 10) if (current_page * 10 + 10) < queue_len else queue_len
        page_display = "\n".join(display_queue[first_page_entry:last_page_entry])

        # create embed
        embed = hikari.Embed(title = f"{utilities.FLAVOR.get('music')} Current Queue ({len(queue)} songs, {get_total_length_of_tracks(queue)} total length)", description = f"{page_display}", color = hikari.Color(0xc38ed5))\
        .set_footer(f"Page [{current_page + 1}/{num_pages}] | loop mode: {'ON' if node.repeat == True else 'OFF'} | loopqueue mode: {'ON' if node.queue_repeat == True else 'OFF'} | Thank you for using Aru.")

        # assemble Previous and Next Page Buttons
        prev_button_to_page = current_page - 1
        next_button_to_page = current_page + 1

        buttons = plugin.app.rest.build_action_row() 
        if not (prev_button_to_page < 0): # check if index out of bounds. if yes, disable the button
            buttons.add_button(2, f"page|{prev_button_to_page}|{unique_id}").set_emoji(hikari.Emoji.parse(utilities.FLAVOR.get('left_arrow'))).add_to_container()
        else:
            buttons.add_button(2, f"invalid|{prev_button_to_page}|{unique_id}").set_emoji(hikari.Emoji.parse(utilities.FLAVOR.get('left_arrow'))).set_is_disabled(True).add_to_container()
        
        if not (next_button_to_page >= num_pages): # check if index out of bounds. if yes, disable the button
            buttons.add_button(2, f"page|{next_button_to_page}|{unique_id}").set_emoji(hikari.Emoji.parse(utilities.FLAVOR.get('right_arrow'))).add_to_container()
        else: 
            buttons.add_button(2, f"invalid|{next_button_to_page}|{unique_id}").set_emoji(hikari.Emoji.parse(utilities.FLAVOR.get('right_arrow'))).set_is_disabled(True).add_to_container()

        return embed, buttons
    
    # Start with first page
    current_page = 0
    embed, buttons = assemble_page(current_page)
    response = await ctx.respond(embed=embed, component=buttons)
    while (new_page := (await respond_to_interaction(30, unique_id, ctx.author.id))) != -1:
        new_embed, new_buttons = assemble_page(new_page)
        await plugin.app.rest.edit_message(channel = ctx.channel_id, message = await response.message(), embed = new_embed, component = new_buttons)

@plugin.command
@lightbulb.option("new_position", "The new queue position you want to move the song to. (1-based indexing)")
@lightbulb.option("current_position", "The current queue position of the song you wish to move. (1-based indexing)")
@lightbulb.command("move", "[🎵] Move a song to a new position in the queue.")
@lightbulb.implements(lightbulb.SlashCommand)
async def move(ctx):
    position = int(ctx.options.current_position) - 1
    new_position = int(ctx.options.new_position) - 1
    node = await lavalink.get_guild_node(ctx.guild_id)
    queue = node.queue
    if not node or not node.queue:
        await ctx.respond("The queue is empty!")
        return
    if position < 1 or position > len(queue) - 1 or new_position < 1 or new_position > len(queue) - 1:
        await ctx.respond(f"Error: Invalid position(s). Must be between `2-{len(node.queue)}`")
        return

    song = queue[position]

    await lavalink.remove(ctx.guild_id, position)
    queue = node.queue
    queue.insert(new_position, song)
    node.queue = queue

    song_display = f"**[{position+1}->{new_position+1}]** [{queue[new_position].title}]({queue[new_position].uri}) ({convert_milliseconds(queue[new_position].length)})"
    string = utilities.FLAVOR.get('secondary_option') + song_display + f" _requested by <@{queue[position].requester}>_" + "\n"

    embed = hikari.Embed(title = f"Song moved", description = string, color = hikari.Color(0xc38ed5))\
                .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
                .set_author(name = f"The following song has been moved to a new position in the queue.", icon = plugin.app.get_me().avatar_url)
    
    await ctx.respond(embed = embed)

@plugin.command
@lightbulb.option("position", "The queue position of the song you wish to remove. (1-based indexing)")
@lightbulb.command("remove", "[🎵] Remove a song from the queue.")
@lightbulb.implements(lightbulb.SlashCommand)
async def remove(ctx):
    position = int(ctx.options.position) - 1
    node = await lavalink.get_guild_node(ctx.guild_id)
    queue = node.queue
    if not node or not node.queue:
        await ctx.respond("The queue is empty!")
        return
    if position < 0 or position > len(queue) - 1:
        await ctx.respond(f"Error: Invalid position. Must be between `1-{len(node.queue)}`")
        return

    if position == 0:
        await skip(ctx)
        return

    song = queue[position]
    song_display = f"**[{position+1}]** [{song.title}]({song.uri}) ({convert_milliseconds(song.length)})"
    string = utilities.FLAVOR.get('secondary_option') + song_display + f" _requested by <@{song.requester}>_" + "\n"

    embed = hikari.Embed(title = f"Song removed", description = string, color = hikari.Color(0xc38ed5))\
                .set_footer(text = f"Requested by {ctx.author.username}#{ctx.author.discriminator}", icon = ctx.author.avatar_url)\
                .set_author(name = f"The following song has been removed from the queue.", icon = plugin.app.get_me().avatar_url)
    
    await lavalink.remove(ctx.guild_id, position)
    await ctx.respond(embed = embed)

@plugin.command
@lightbulb.command("np", "[🎵] Check what song is currently playing.")
@lightbulb.implements(lightbulb.SlashCommand)
async def np_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("Nothing is playing right now!")
        return
    await ctx.respond(f"[{node.queue[0].title}]({node.queue[0].uri})")

@plugin.command
@lightbulb.command("loop", "[🎵] Toggle loop mode on/off", aliases=["l", "repeat"])
@lightbulb.implements(lightbulb.SlashCommand)
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

@plugin.command
@lightbulb.command("loopqueue", "[🎵] Toggle loop queue mode on/off.", aliases=["lq", "repeat_queue", "repeat_q"])
@lightbulb.implements(lightbulb.SlashCommand)
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

@plugin.command
@lightbulb.command("shuffle", "[🎵] Shuffle the queue!")
@lightbulb.implements(lightbulb.SlashCommand)
async def shuffle_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("The queue is empty!")
        return
    await lavalink.shuffle(ctx.guild_id)
    await ctx.respond("Shuffled the music!")

@plugin.command
@lightbulb.command("leave", "[🎵] Leave the voice channel.")
@lightbulb.implements(lightbulb.SlashCommand)
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