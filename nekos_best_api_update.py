import requests
import datetime

# run this file to update gif files from nekos_best_api
author_id = 173555466176036864

action_files = {
        'bonk':'action_bonk_gifs.txt',
        'blush': 'action_blush_gifs.txt',
        'cuddle': 'action_cuddle_gifs.txt',
        'highfive': 'action_highfive_gifs.txt',
        'holdhands': 'action_holdhands_gifs.txt',
        'hug': 'action_hug_gifs.txt',
        'kiss': 'action_kiss_gifs.txt',
        'nom': 'action_nom_gifs.txt',
        'nuzzle': 'action_nuzzle_gifs.txt',
        'pat': 'action_pat_gifs.txt',
        'poke': 'action_poke_gifs.txt',
        'slap': 'action_slap_gifs.txt',
        'stare': 'action_stare_gifs.txt', 
    }

nekos_best_api_actions = {
    'blush': 'blush',
    'cuddle': 'cuddle',
    'holdhands': 'handhold',
    'highfive': 'highfive',
    'hug': 'hug',
    'kiss': 'kiss',
    'pat': 'pat',
    'poke': 'poke',
    'slap': 'slap',
    'stare': 'stare',
}

for k,v in nekos_best_api_actions.items():
    max_number_of_gifs = int(requests.get("https://nekos.best/api/v2/endpoints").json()[v]['max'])
    for i in range(0,max_number_of_gifs):
        num = str(i).zfill(3)
        gif_link = "https://nekos.best/api/v2/" + v + f"/{num}" + ".gif"
        f = open(action_files.get(k), 'r')
        already_added = False
        for j in f.readlines(): # iterate through relevant file
            x ={j.split("|")[2][:-1]}
            print(f"{x} vs. {gif_link}")

            if j.split("|")[2][:-1] == gif_link: # if gif link found, break
                already_added = True
                break
        if already_added: # if gif link found, close file and continue to next gif
            f.close()
            continue
        else: # otherwise add it
            f = open(action_files.get(k), 'a')
            new_line = str(datetime.datetime.now())[:-7] + '|' + str(author_id) + '|' + gif_link
            f.write(new_line)
            f.write("\n")
        


