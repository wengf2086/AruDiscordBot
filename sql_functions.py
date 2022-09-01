import sqlite3
import datetime
from venv import create

# Connection Object that represents our database. Can pass in a file or have an in-memory database with "_:memory:_"
# Creates a file or connects to it if it already exists
# conn = sqlite3.connect('.\sqlite\bot.db')

# Cursor that allows us to execute SQL commands
# c = conn.cursor()

class Gif():
    @staticmethod
    def add_gif(action_name = str, author_id = int, gif_link = str, date = None):
        '''Adds a gif link to the database.'''
        if date == None:
            date = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            conn = sqlite3.connect(db_dir)
        insert_gif(action_name, date, author_id, gif_link)

    @staticmethod
    def get_random_gif(action_name = str):
        '''Get a random GIF object from the database.'''
        gif = get_random_gif(action_name)
        return Gif(gif[0], gif[1], gif[2], gif[3], gif[4], gif[5], gif[6], gif[7], gif[8])

    @staticmethod
    def get_gif_from_link(gif_link = str):
        '''Get a specific GIF object from the database.'''
        gif = get_specific_gif(gif_link)
        if gif == None:
            return None

        return Gif(gif[0], gif[1], gif[2], gif[3], gif[4], gif[5], gif[6], gif[7], gif[8])

    def __init__(self, action_name = str, date_added = str, author_id = int, link = str, appearances = int, likes = int, dislikes = int, reports = int, is_disabled = int):
        self.action_name = action_name
        self.date_added = date_added
        self.author_id = author_id
        self.link = link
        self.appearances = appearances
        self.likes = likes
        self.dislikes = dislikes
        self.reports = reports
        self.is_disabled = True if is_disabled else False

    def incr_appearance(self):
        '''Increments this gif's 'appearance' attribute by 1 in the database.'''
        gif_appearance(self.link)

    def incr_likes(self):
        '''Increments this gif's 'likes' attribute by 1 in the database.'''
        gif_upvote(self.link)

    def incr_dislikes(self):
        '''Increments this gif's 'dislikes' attribute by 1 in the database.'''
        gif_downvote(self.link)
    
    def incr_reports(self):
        '''Increments this gif's 'reports' attribute by 1 in the database.'''
        gif_report(self.link)

    def disable(self):
        '''Enables/Disables this gif in the database.'''
        disable_gif(self.link)

# Should only be called once
# Creates the GIFS table:
# col 0: action_name
# col 1: date_added, datetime.datetime.now().strftime("%m/%d/%y, %H:%M:%S")
# col 2: author_id
# col 3: link
# col 4: appearances
# col 5: likes
# col 6: dislikes
# col 7: reports
# col 8: is_disabled
db_dir = './bot.db'

def create_gifs_table():
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    with conn:
        c.execute("""CREATE TABLE gifs(
                    action_name text NOT NULL,
                    date_added text NOT NULL,
                    author_id integer NOT NULL,
                    link text NOT NULL UNIQUE,
                    appearances integer DEFAULT 0,
                    likes integer DEFAULT 0,
                    dislikes integer DEFAULT 0,
                    reports integer DEFAULT 0,
                    is_disabled integer DEFAULT 0
                    )""")

def delete_gifs_table():

    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    with conn:
        c.execute("""DROP TABLE gifs""") 

def insert_gif(action_name, date, author_id, gif_link):
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    with conn:
        c.execute("""INSERT INTO gifs(action_name, date_added, author_id, link) 
        VALUES (:action_name, :date, :author_id, :gif_link)
        """, {'action_name': action_name, 'date': date, 'author_id': author_id, 'gif_link': gif_link})

def get_random_gif(action_name):
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    c.execute("SELECT * FROM gifs WHERE action_name=:action_name and is_disabled = 0 ORDER BY RANDOM() LIMIT 1", {'action_name':action_name})
    return c.fetchone() # Returns None if none found

def get_specific_gif(gif_link):
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    c.execute("SELECT * FROM gifs WHERE link=:gif_link", {'gif_link':gif_link})
    return c.fetchone() # Returns None if none found

def gif_appearance(gif_link):
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    with conn:
        c.execute("UPDATE gifs SET appearances = appearances + 1 WHERE link=:gif_link", {'gif_link': gif_link})

    conn.close()

def gif_upvote(gif_link):
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    with conn:
        c.execute("UPDATE gifs SET likes = likes + 1 WHERE link=:gif_link", {'gif_link': gif_link})

    conn.close()

def gif_downvote(gif_link):
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    with conn:
        c.execute("UPDATE gifs SET dislikes = dislikes + 1 WHERE link=:gif_link", {'gif_link': gif_link})
    conn.close()

def gif_report(gif_link):
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    with conn:
        c.execute("UPDATE gifs SET reports = reports + 1 WHERE link=:gif_link", {'gif_link': gif_link})
    conn.close()

def disable_gif(gif_link):
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    with conn:
        # get the current is_disabled value of the GIF and reverse it
        c.execute("SELECT * FROM gifs WHERE link=:gif_link", {'gif_link': gif_link})
        gif = c.fetchone()
        currently_disabled = gif[8] 
        new_value = 0 if currently_disabled else 1
        c.execute("UPDATE gifs SET is_disabled = :new_value WHERE link=:gif_link", {'new_value': new_value, 'gif_link': gif_link})
    conn.close()

def print_all_gifs():
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    c.execute("SELECT * FROM gifs")
    for row in c.fetchall():
        print(row)
    conn.close()
