import sqlite3
from datetime import datetime
from ssl import create_default_context
from venv import create

db_dir = './bot.db'

class Gif():
    @staticmethod
    def add_gif(action_name = str, author_id = int, gif_link = str, date = None):
        '''
        Adds a gif link to the database.
        date_added format: ("%m/%d/%y, %H:%M:%S")'''
        if date == None:
            date = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
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

# GIF Database Functiions
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
    '''date_added format: ("%m/%d/%y, %H:%M:%S")'''
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

# Feedback Log Database Functions
def create_feedback_log_table():
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    with conn:
        c.execute("""CREATE TABLE feedback_log(
                    feedback_type text NOT NULL,
                    date_added text NOT NULL,
                    author_id integer NOT NULL,
                    info text NOT NULL
                    )""") # info: Either feedback or gif_link

def add_feedback(feedback_type = str, date = None, author_id = int, info = str):
    '''
    feedback_type: 'upvote', 'downvote', 'report', 'disable', 'comment', 'nsfw', 'wrong_cat', 'broken'.
    date format: ("%m/%d/%y, %H:%M:%S")
    info: gif link or comment'''

    if date == None:
        date = datetime.strftime(datetime.now(), "%m/%d/%y, %H:%M:%S")

    if feedback_type != None and feedback_type not in ['upvote', 'downvote',  'disable', 'comment', 'nsfw', 'wrong_cat', 'broken']:
        raise Exception(f"Invalid feedback_type '{feedback_type}'. Must be 'upvote', 'downvote', 'report', 'disable', or 'comment'.")
    
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    with conn:
        c.execute("""INSERT INTO feedback_log(feedback_type, date_added, author_id, info) 
        VALUES (:feedback_type, :date, :author_id, :info)
        """, {'feedback_type': feedback_type, 'date': date, 'author_id': author_id, 'info': info})

def fetch_todays_feedback(feedback_type = None, author_id = None):
    today = datetime.strftime(datetime.now(), "%m/%d/%y")
    return fetch_feedback(feedback_type = feedback_type, date = today, author_id = author_id)

def fetch_feedback(feedback_type = None, date = None, author_id = None):
    '''Returns feedback based on specified parameters, or all feedback if no parameters are specified.
    date format: ("%m/%d/%y")'''
    if feedback_type != None and feedback_type not in ['upvote', 'downvote', 'disable', 'comment', 'nsfw', 'wrong_cat', 'broken']:
        raise Exception(f"Invalid feedback_type '{feedback_type}'. Must be 'upvote', 'downvote', 'disable', 'comment', 'nsfw', 'wrong_cat', 'broken'.")
    if date != None:
        try:
            date_added = datetime.strptime(date, "%m/%d/%y").strftime("%m/%d/%y")
        except:
            return Exception(f"Invalid date format. Must be \"%m/%d/%y\"")

    conn = sqlite3.connect(db_dir)
    c = conn.cursor()
    if author_id == None and feedback_type == None:
        c.execute("SELECT * FROM feedback_log")
    
    elif author_id != None and feedback_type != None: # If both author_id and feedback_type requested
        c.execute("SELECT * FROM feedback_log WHERE feedback_type=:feedback_type AND author_id=:author_id", {'feedback_type':feedback_type, 'author_id':author_id})

    elif feedback_type != None: # If author_id not requested
        c.execute("SELECT * FROM feedback_log WHERE feedback_type=:feedback_type", {'feedback_type':feedback_type})
    
    elif author_id != None: # IF feedback_type not requested
        c.execute("SELECT * FROM feedback_log WHERE author_id=:author_id", {'author_id':author_id})
    
    all_feedback = c.fetchall() # Returns None if none found

    feedback_from_date = []
    if date != None:
        for feedback in all_feedback:
            if datetime.strptime(feedback[1], "%m/%d/%y, %H:%M:%S").strftime("%m/%d/%y") == date_added:
                feedback_from_date.append(feedback)
        return feedback_from_date
    else:
        return all_feedback

print(fetch_todays_feedback(feedback_type = "broken"))