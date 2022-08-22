import requests
import datetime
import os.path

# run this file to update gif files from nekos_best_api
author_id = 173555466176036864

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

f = None
for k,v in nekos_best_api_actions.items():
    max_number_of_gifs = int(requests.get("https://nekos.best/api/v2/endpoints").json()[v]['max'])
    for i in range(0,max_number_of_gifs):
        num = str(i).zfill(3)
        gif_link = "https://nekos.best/api/v2/" + v + f"/{num}" + ".gif"
        if not os.path.exists("C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/" + f"action_{k}_gifs.txt"):
            f = open("C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/" + f"action_{k}_gifs.txt", 'w')
            f.close()
        
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
            f.write(new_line)
            f.write("\n")

f.close()
print("All done! x)")
        


