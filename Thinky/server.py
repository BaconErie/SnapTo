from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
active_games = 

@app.route('/ping')
def ping():
    return '', 204

@socket.on('createGame')
def create_game(json):


app.run()