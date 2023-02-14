# Aru Discord Bot
This is my Discord Bot, Aru!

Made by me, cookie#0837, on Discord. Feel free to add me and ask me any questions you might have about my bot.

~~[Invite Aru](https://discord.com/api/oauth2/authorize?client_id=1009180210823970956&permissions=8&scope=applications.commands%20bot) to your server!~~
Many of Aru's commands are now broken / outdated due to changes in Discord's API, but some functions still work (like Action Commands). I'll be working on a new bot soon, so if you've enjoyed using Aru, thank you for your support and please look forward to my next project!

## What does Aru do?
Aru is an aesthetic, anime-themed multi-purpose Discord bot with "action" commands, music commands, info commands, and more!
* Lilac-purple themed
* Cute animated custom emojis and buttons
* User-friendly UI
* Interactive and collaborative GIF database (see below for more info!)

### Action Commands
The action command allows a user to specify an action (e.g., "blush", "slap", "wink") and direct it towards another user. Aru will then fetch a random anime gif from the database corresponding to the specified action and send it to the channel that the command was used in, along with a message describing what action has been performed, mentioning both the actor and recipient of the action. Here's an example:

![action command example image](/images/action_command_example.png)
![action command example2 image](/images/action_command_example_2.png)

See? Fun for everyone!
* If you're not sure what actions are available for use, don't worry! When you input the action name, there'll be a dropdown menu that you can select from.

#### Adding a GIF to the database
One of Aru's shining features is that users can contribute their own GIFs to the database that she fetches GIFs from! To do so, a user can use the /addgif command, like so:

![addgif command example image](/images/addgif_command_example.png)
![addgif command example2 image](/images/addgif_command_example_2.png)

#### Liking and Disliking a GIF
Users are able to like or dislike GIFs that they encounter. This feedback will be used to improve and update the database.

#### Reporting a GIF
If a user encounters a GIF that is NSFW, in the wrong category, or broken, they can report it using the "Report this GIF" button. The user will be able to select a reason for the report:
![report example image](/images/report_example.png)

Once a report has been made, the GIF will be deleted and the report will be logged in the database. Upon review, the GIF will either be fixed or removed, depending on the report reason.

### Music Commands
What's a multi-purpose Discord bot without music commands? Aru allows you to query and play tracks from YouTube (and soon, Spotify as well!):

![query example image](/images/query_example.png)

Viewing the queue:

![queue example image](/images/queue_example.png)

#### All Music Commands: 
play, stop, pause, resume, seek, queue, np, move, remove, repeat, shuffle, leave

I'm also thinking about creating an interactive music player with buttons so that users don't have to type commands to pause, resume, repeat, shuffle, and loop the queue. We'll see when I can get to that.

### Info Commands
Aru also provides info commands that will show information about a user or server, fetch a user's profile picture, or provide an explanation about a specific command.

#### Getting User Information
Displays information about the specified user. Information available depends on whether or not the user is a member of the current server.

Command: /info user user:@user#tag

![info user example image](/images/info_user_example.png)

#### Getting Server Information
Displays information about the current server.

Command: /info server

![info server example image](/images/info_server_example.png)

#### Getting Command Information
Displays information about a specific command and its usage.

Coming soon!

#### Getting a User's Avatar
Fetchs the specified user's profile picture and URL (or the author's profile picture if no user is specified).

Command: /info avatar user:@user#tag

![info avatar example image](/images/info_avatar_example.png)

### Feedback Command
Users can provide feedback about Aru using the /feedback command. All feedback is read by me and helps to improve Aru. I appreciate any feedback that you have!

### Other commands
Aru has other fun commands as well (like a reaction bomb command and an 8-ball command). 
To see a full list of commands, use the command:
/info help
![info help example image](/images/info_help_example.png)

### Thanks for using Aru!
Here's a little tidbit about Aru's creation.
I made Aru for a few reasons:
1. There are many other bots out there, but they all had features that I felt like could be improved on.
2. The UIs for other bots were ugly.
3. I'm on the E-Board for a club for my school, and I thought that making a bot to manage online events would be fun and also make things a lot easier. Here are some things that Aru will soon be able to do:
* Make announcements (Actually, I've already implemented this lol)
* Break people up into different voice channels
* Temporarily modify voice channel names to match a club activity
* Create temporary text channels for a club activity with descriptions that explain the club activity
4. I taught myself Python a week before making Aru, and I got excited when I learned that there were python APIs available to create discord bots. I wanted to test my skills and expand my knowledge, so here I am!

Making Aru was honestly so fun and fulfilling. I implemented a lot more functions for her than I initially anticipated, and I have many more plans for her. 

Special thanks to:
* hikari devs for making a straightfoward API
* hikari Support Server for general support
* Antimatter#2557 for helping me with music commands

Making Aru would still have been possible, but A LOT harder if it weren't for the people above. So... thank you for your patience, kindness, and helpfulness! :3c







