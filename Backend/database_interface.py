import sqlite3

connection=sqlite3.connect("user_messaging_system.db")

cursor=connection.cursor() 

#Create messages table
cursor.execute("""CREATE TABLE IF NOT EXISTS messages(
               message_id INTEGER PRIMARY KEY AUTOINCREMENT,
               client_username TEXT NOT NULL,
               message TEXT NOT NULL
)""")

#Create users table
cursor.execute("""CREATE TABLE IF NOT EXISTS users( 
               username TEXT NOT NULL UNIQUE,
               password TEXT NOT NULL
)""")

#Create index to quickly get users corresponding to messages
cursor.execute("CREATE INDEX IF NOT EXISTS users_index ON messages(client_username)")

#Takes in username and message, adds to messages table
def add_message_to_db(username, message):
    #Check if username is existing user
    cursor.execute("SELECT * FROM users WHERE username=:username",(username,))
    result=cursor.fetchone()
    if result is None:
        print("User does not exist!")
        return
    
    cursor.execute("INSERT INTO messages(client_username, message) Values(:username, :message)",(username, message))
    connection.commit()

#Takes in a user, clears their messages from messages table
def clear_user_messages_from_db(user):
    cursor.execute("DELETE FROM messages WHERE client_username = :username",(user,))
    connection.commit()
  
#Adds user to db. Return True if succesful, False otherwise
def add_user_to_db(username, password):
    cursor.execute("SELECT * FROM users WHERE username=:username",(username,))
    result=cursor.fetchone()
    if result is not None:
        print("Username taken!")
        return False 
    
    cursor.execute("INSERT INTO users(username, password) Values(:username, :password)",(username,password))
    connection.commit()
    print("user succesfully registered!")
    return True

#Checks if user exists in the database.
def authenticate_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username=:username AND password=:password",(username,password))
    result=cursor.fetchone()
    if result is not None:
        print("User logged in!")
        return True
    print("User does not exist!")
    return False

def delete_all_users():
    cursor.execute("DELETE FROM users")
    connection.commit()
