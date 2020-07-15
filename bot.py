# Twitch Chat Bot Configuration File
from config import TMI_TOKEN, CLIENT_ID, BOT_NICK, BOT_PREFIX, CHANNEL, DB

# Sqlite Interface
import sqlite3

# Global database connection variable
conn = None

# Allows code to run when script is terminated
import atexit

# Twitch Chat Bot Interface
from twitchio.ext import commands

# Create the bot using the configuration presets
bot = commands.Bot(
    # Set up the bot
    irc_token=TMI_TOKEN,
    client_id=CLIENT_ID,
    nick=BOT_NICK,
    prefix=BOT_PREFIX,
    initial_channels=[CHANNEL]
)

def start_db():

    print ('Bot started, connecting to db ...')

    # Use global connection variable
    global conn

    # Connect to the database
    try:

        # Connect and create new table
        conn = sqlite3.connect('sets.db')

        # Create query object
        c = conn.cursor()

        # Execute table creation query
        c.execute('CREATE TABLE IF NOT EXISTS SETS (USER TEXT, CHANNEL TEXT, DATA TEXT)')

        # Commit the change to the database
        conn.commit()

    except Exception as e:
        print('Failed to connect to database! Reason:', e)

def close_db():

    print('Bot stopped, closing db connection ...')

    # Use global connection variable
    global conn

    # If conn is connected
    if conn:
        # Commit all changes
        conn.commit()

        # Close the connection
        conn.close()

        # Null out the variable
        conn = None

@bot.event  # Channel message event
async def event_message(ctx):
    # Dereference the message text
    message = ctx.content

    # Dereference the message sender
    meta = str(ctx._author)

    # If the request is for a pokemon set
    if message.startswith('$trade '):

        # Print the set to the terminal
        set = message.split('$trade ')[1]

        # Retrieve the user / channel from the message
        name, channel = meta.replace('<User', '').replace('>', '').strip().split(' ')

        # Split the name from the tag
        name = name.split('=')[1]

        # Split the channel from the tag
        channel = channel.split('=')[1]

        # If we are connected to the database
        if conn:
            # Create database query
            c = conn.cursor()

            # Execute database insert query for set
            c.execute('INSERT INTO SETS VALUES ("' + name + '","' + channel + '","' + set + '")')

            # Report that a set was inserted
            print('Set for',name,'on channel',channel,'was inserted.');

        else:
            # Print the message metadata
            print(name, channel, set)


# If this file is not exported as a module
if __name__ == '__main__':

    # Close the database when we close the script
    atexit.register(close_db)

    # Open the database connection
    start_db()

    # Run the bot
    bot.run()
