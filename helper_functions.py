import os.path
from os import listdir

# Functions to be accessed by any file that needs them

def get_all_action_names():
    onlyfiles = [f for f in listdir("C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/") if os.path.isfile(os.path.join("C:/Users/Cookie/Documents/GitHub/AruDiscordBot/action_gifs/", f))]
    action_names = []
    for file in onlyfiles:
        name = file.split("_")[1]
        action_names.append(name)

    return action_names