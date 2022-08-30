import requests
import datetime
import os.path

# Run this file to update the actions with GIFs from nekos.best API.
author_id = 173555466176036864

# This bot has different names for actions; this dictionary serves as a translator.
# bot_action_name : nekos_api_action_name
nekos_best_api_actions = {
    'blush': 'blush',
    'cuddle': 'cuddle',
    'holdhands': 'handhold',
    'highfive': 'highfive',
    'hug': 'hug',
    'kick': 'kick',
    'kiss': 'kiss',
    'laugh': 'laugh',
    'pat': 'pat',
    'poke': 'poke',
    'punch':'punch',
    'shoot': 'shoot',
    'slap': 'slap',
    'stare': 'stare',
    'wink': 'wink',
    'yeet': 'yeet'
}

# Iterate through each item in the dictionary
for k,v in nekos_best_api_actions.items():
    max_number_of_gifs = int(requests.get("https://nekos.best/api/v2/endpoints").json()[v]['max']) # Get the number of gifs for each nekos_best API action
    for i in range(0,max_number_of_gifs): # for each gif
        num = str(i).zfill(3) # pad the index to get 3 digits (formatting)
        gif_link = "https://nekos.best/api/v2/" + v + f"/{num}" + ".gif" # append the padded index to create the link for the gif

        # if no file exists for the current action, create one
        if not os.path.exists("C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/" + f"action_{k}_gifs.txt"):
            f = open("C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/" + f"action_{k}_gifs.txt", 'w')
            f.close()
        
        # check the file to see if the current GIF already exists
        f = open("C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/" + f"action_{k}_gifs.txt", 'r')
        already_added = False
        for j in f.readlines(): # iterate through relevant file
            x ={j.split("|")[2][:-1]}

            if j.split("|")[2][:-1] == gif_link: # if gif link found, break
                already_added = True
                break
        if already_added: # if gif link found, close file and continue to next gif
            f.close()
            continue
        else: # otherwise add it
            f = open("C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/" + f"action_{k}_gifs.txt", 'a')
            new_line = str(datetime.datetime.now())[:-7] + '|' + str(author_id) + '|' + gif_link
            print(f"{k}: Added '{gif_link}'")
            f.write(new_line)
            f.write("\n")

f.close()
print("All done! x)")
        


