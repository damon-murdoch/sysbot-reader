# Twitch Chat Bot Configuration File
from config import TMI_TOKEN, CLIENT_ID, BOT_NICK, BOT_PREFIX, CHANNEL, DB, LOG

# Sqlite Interface
import sqlite3

# Datetime library (for timestamp)
from datetime import datetime

# Global database connection variable
conn = None

# Global Logging file
log = None

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
    initial_channels=CHANNEL
)

# Used for reporting to text and
# command line log in one statement
def report(message):

    # Use global log reference
    global log

    # Create the output timestamp message
    msg = '[' + timestamp() + '] ' + message + '\n'

    # If the log file is declared
    if log:
        # Write to it
        log.write(msg)

    # Print log message to terminal (without adding newline)
    print(msg,end='')

# Generates a timestamp for the current
# system time and returns it
def timestamp():

    # Retrieve the current time
    time = datetime.now();

    # Convert current time to timestamp
    timestamp = time.strftime('%d-%m-%y %H:%M:%S');

    # Return the timestamp object
    return timestamp


def start_db():

    # Use global connection / log variables
    global conn,log

    # Connect to the log file
    try:

        # Open the log file
        log = open(LOG,'a')

        report('Log file opened successfully.')

    # Failure opening log file
    except Exception as e:

        # Report failure to terminal
        report('Failed to open log file! Reason: ' + str(e))

    # Connect to the database
    try:

        # Connect and create new table
        conn = sqlite3.connect('sets.db')

        # Create query object
        c = conn.cursor()

        # Execute table creation query
        c.execute('CREATE TABLE IF NOT EXISTS SETS (USER TEXT, CHANNEL TEXT, DATA TEXT, TIME TEXT)')

        # Commit the change to the database
        conn.commit()

        # Log that the connection was successful.
        report('Database connection successful.')

    # Fail to connect to the database file
    except Exception as e:
        report('Failed to connect to database! Reason: ' + str(e))

def close_db():

    report('Bot stopped, closing db connection ...')

    # Use global connection variable
    global conn, log

    # If conn is connected
    if conn:
        # Commit all changes
        conn.commit()

        # Close the connection
        conn.close()

        # Null out the variable
        conn = None

    # If the log file is open
    if log:
        # Close it
        log.close()

        # Null out the variable
        log = None

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
            c.execute('INSERT INTO SETS VALUES ("' + name + '","'  + channel + '","' + set + '","' + timestamp() + '")')

            # Report that a set was inserted
            report('Set for ' + name + ' on channel ' + channel + ' was inserted.')

        # Database connection failed
        else:
            # Log the inserted row to the command line 
            report('("' + name + '","'  + channel + '","' + set + '","' + timestamp() + '")')


# If this file is not exported as a module
if __name__ == '__main__':

    # Close the database when we close the script
    atexit.register(close_db)

    # Open the database connection
    start_db()

    # Run the bot
    bot.run()
