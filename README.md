# AruDiscordBot
This is my Discord Bot, Aru!
Made by me, cookie#0837 on Discord. Feel free to add me and ask me any questions you might have about my bot.
[Invite Aru](https://discord.com/api/oauth2/authorize?client_id=1009180210823970956&permissions=8&scope=applications.commands%20bot) to your server!

## What does Aru do?
Aru is an aesthetic, anime-themed multi-purpose Discord bot with "action" commands, music commands, info commands, and more!
* Lilac-purple themed
* Cute custom emojis and buttons
* User-friendly UI
* Interactive and collaborative database (see below for more info!)

### Action Commands
The /action command allows a user to specify an action, e.g., "blush", "slap", "wink", and direct it towards another user. Aru will fetch a random anime gif from her database corresponding to the specified action and send it to the channel that the command was used in, along with a message describing what action has been performed, mentioning both the actor and recipient of the action. Here's an example:

![action command example image](/images/action_command_example.png)
![action command example2 image](/images/action_command_example_2.png)

See? Fun for everyone!
* If you're not sure what actions are available for use, don't worry! When you input the action name, there'll be a dropdown menu that you can select from.

#### Adding a GIF to the database
One of Aru's shining features is that she allows users to contribute their own GIFs to the database that she fetches GIFs from! To do so, a user can use the /addgif command, like so:

![addgif command example image](/images/addgif_command_example.png)
![addgif command example2 image](/images/addgif_command_example_2.png)

#### Liking and Disliking a GIF
Users are able to like or dislike GIFs that they encounter. This feedback will be used to improve and update the database.

#### Reporting a GIF
If a user encounters a GIF that is NSFW, in the wrong category, or broken, they can report it using the "Report this GIF" button. The user will be able to choose the reason for the report:
![report example image](/images/report_example.png)
Once a report has been made, the GIF will be deleted and the report will be logged in the database. Upon review, the GIF will either be fixed or removed, depending on the report reason.

### Music Commands
What's a multi-purpose Discord bot without music commands? 
Aru's music commands use custom emojis and buttons to make them more user-friendly and pleasuring to the eye. I'm pretty proud of them :)
Aru allows you to query and play tracks from YouTube (and soon, Spotify as well!):
![query example image](/images/query_example.png)

Viewing the queue:
![queue example image](/images/queue_example.png)

Here's a list of all the music commands available: play, stop, pause, resume, seek, queue, np, move, remove, repeat, shuffle, leave

I'm also thinking about creating an interactive music player with buttons so that users don't have to type commands to pause, resume, repeat, shuffle, and loop the queue. We'll see when I can get to that.

### Info Commands
Aru also provides /info commands that will show information about a user or server:

#### Getting User Information
Displays information about the specified user. Information available depends on whether or not the user is a member of the current server.

Command: /info user user:@user#tag
![info user example image](/images/info_user_example.png)

#### Getting Server Information
Displays information about the current server.

Command: /info server
![info server example image](/images/info_server_example.png)

#### /info command command_name:command
Displays information about a specific command and its usage.

Coming soon!

#### /info avatar user:@user#tag
Fetchs the specified user's profile picture and URL (or the author's profile picture if no user is specified).

Command: /info avatar user:@user#tag
![info avatar example image](/images/info_avatar_example.png)

### Feedback Command
Users can provide feedback about Aru using the /feedback command. All feedback is read by me and helps to improve Aru. I appreciate any feedback that you have!

### Other commands
Aru has other fun commands as well (like a reaction bomb command and an 8-ball command). To see a full list of commands, use the command:
/info help
![info help example image](/images/info_help_example.png)












