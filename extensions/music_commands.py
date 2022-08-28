import lightbulb
import hikari
import lavaplayer
import logging
import asyncio

plugin = lightbulb.Plugin('music_commands')

# Lavalink object
lavalink = lavaplayer.Lavalink(
    host="78.108.218.93",
    port=25538,
    password="mysparkedserver",
    user_id=173555466176036864
)

# Connect Lavalink when Bot Starts
@plugin.listener(hikari.StartedEvent)
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

# Commands
@plugin.command 
@lightbulb.command('music', 'Play music!')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def music(ctx):
    pass

@music.child
@lightbulb.command("join", "Join your voice channel.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def join(ctx):
    states = plugin.app.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]
    if not voice_state:
        await ctx.respond("You are not in a voice channel. Join one first!")
        return
    channel_id = voice_state[0].channel_id
    await plugin.app.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    await lavalink.wait_for_connection(ctx.guild_id)
    await ctx.respond(f"Joined <#{channel_id}>!")

@music.child
@lightbulb.option("query", "Search for a song or input a YouTube link")
@lightbulb.command("play", "Play a song!", aliases=["p"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def play(ctx):
    query = ctx.options.query
    result = await lavalink.auto_search_tracks(ctx.options.query)  # search for the query
    if not result:
        await ctx.respond("No result found for the specified query. Please try again.")
        return
    elif isinstance(result, lavaplayer.TrackLoadFailed):
        await ctx.respond("Track load failed, try again later.\n```{}```".format(result.message))
        return
    elif isinstance(result, lavaplayer.PlayList):
        await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
        await ctx.respond(f"Added {len(result.tracks)} tracks to queue!")
        return 

    await lavalink.play(ctx.guild_id, result[0], ctx.author.id)  # play the first result
    await ctx.respond(f"[{result[0].title}]({result[0].uri})")  # send the embed

@music.child
@lightbulb.command("stop", "Stop the player!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def stop(ctx):
    await lavalink.stop(ctx.guild_id)
    await ctx.respond("Stopped the current song.")

@music.child
@lightbulb.command("pause", "Pause the current song!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def pause(ctx):
    await lavalink.pause(ctx.guild_id, True)
    await ctx.respond("Music paused!")

@music.child
@lightbulb.command("resume", "Resume playing the current song!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def resume(ctx):
    await lavalink.pause(ctx.guild_id, False)
    await ctx.respond("Music resumed!")

@music.child
@lightbulb.option("position", "Position to seek")
@lightbulb.command("seek", "Seek a position in the song!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def seek(ctx):
    position = ctx.options.position
    await lavalink.seek(ctx.guild_id, position)
    await ctx.respond(f"Position {position} seeked!")

@music.child
@lightbulb.option("vol", "Volume to set to")
@lightbulb.command("volume", "Set my volume!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def volume(ctx):
    volume = ctx.options.vol
    await lavalink.volume(ctx.guild_id, volume)
    await ctx.respond(f"Set volume to {volume}%")

@music.child
@lightbulb.command("destroy", "Destroy!!!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def destroy(ctx):
    await lavalink.destroy(ctx.guild_id)
    await ctx.respond("Destroy.. the bot?")

@music.child
@lightbulb.command("queue", "Display the current queue")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def queue(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    embed = hikari.Embed(
        description="\n".join(
            [f"{n+1}- [{i.title}]({i.uri})" for n, i in enumerate(node.queue)])
    )
    await ctx.respond(embed=embed)

@music.child
@lightbulb.command("np", "Check what song is currently playing.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def np_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("nothing playing")
        return
    await ctx.respond(f"[{node.queue[0].title}]({node.queue[0].uri})")

@music.child
@lightbulb.command("repeat", "Toggle repeat mode!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def repeat_command(ctx):
    node = await lavalink.get_guild_node(ctx.guild_id)
    stats = False if node.repeat else True
    await lavalink.repeat(ctx.guild_id, stats)
    if stats:
        await ctx.respond("Now repeating this song.")
        return
    await ctx.respond("Stopped repeating this song.")

@music.child
@lightbulb.command("shuffle", "Shuffle the queue!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def shuffle_command(ctx):
    await lavalink.shuffle(ctx.guild_id)
    await ctx.respond("Shuffled the music!")

@music.child
@lightbulb.command("leave", "Leave the voice channel.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def leave_command(ctx):
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
    print("test")
    bot.add_plugin(plugin)
    lavalink.connect()