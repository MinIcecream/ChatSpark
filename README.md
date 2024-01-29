
# 🤖 Chatspark

A conversational companion app that delivers prompts during conversations to prevent awkward silences!
 
 &nbsp;
## 🔨 Made With:

**Client App:** Flutter

**Backend Server:** Python, SQLite3

**API Interfacing:** WebSockets, Azure STT, OpenAI API

&nbsp;



## 📱 How to Use the App
    1. Sign in or register with a username and password.

    2. Click the 'record' button.

    3. If at any time you run out of things to say, say the keyword (by default it's 'hello').

    4. The app will play a response for you to use!


&nbsp;

## 🔍 How it Works

**User Authentication:**  

    1. The Flutter app connects to the WebSocket server upon being opened. 

    2. Once the user enters their credentials and clicks the 'Authenticate' button, their info is sent to 
    the server. 

    3. The server verifies this info with the database and returns a message to the app.

    4. If the app receives a 'success' message, the user is granted access.



**Prompt Generation:**

    1. The user clicks the 'record button.'

    2. Live audio from the microphone is streamed to the WebSocket server.

    3. The WebSocket server feeds this raw data to the Azure STT API.

    4. When the Azure API transcribes a message, it saves it to a temporary db and calls the OpenAI API
    to generate a new prompt.

    5. If at any point Azure API detects the 'keyword', it sends it to the app, which plays it out loud.


&nbsp;



## 💾  Running it Locally

Clone the project

```
git clone https://github.com/MinIcecream/ChatSpark
```
 
&nbsp;

Create two .env files and add your API keys and local IP address to them (examples are provided)

```
.env

ChatSpark/.env
```
 
&nbsp;

Run the WebSocket server

```
python websocket_server.py
```

&nbsp;

Run the Flutter app and voila!

&nbsp;
## 💬   Insights

This project was created as an educational tool for me to learn more about APIs, mobile app development, and databases. 

I had a lot of fun making it, and I hope others will enjoy it!

