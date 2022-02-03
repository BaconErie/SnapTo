from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit, disconnect
from random import randint, sample
from classes import Player, Game
from time import sleep

app = Flask(__name__)
socket = SocketIO(app)
active_games = {}

####################
# HELPER FUNCTIONS #
####################

def generate_game_code():
    new_game_code = randint(100000, 999999)
    if new_game_code in active_games.keys():
        # Duplicate game code, recursively generate until one is found
        new_game_code = generate_game_code()
    
    return new_game_code

def setup_boards(game):
    original_terms = game.terms
    randomized_terms = sample(original_terms, len(original_terms))

    current_board = []
    for term in randomized_terms:
        current_board.append(term)

        if len(current_board) == 9:
            # Max number of terms possible in current_board
            # Add that to boards and clear current_board
            game.boards.append(current_board)
            current_board = []
    
    if len(current_board) != 0:
        # Still stuff in current board. Add it to boards
        game.boards.append(current_board)

def pick_board(game):
    index = randint(0, len(game.boards))
    game.current_board = game.boards[index]
    game.boards.pop(index) # Remove the currently displayed board from boards
    
##################
# MAIN GAME LOOP #
##################

async def game_loop(game_code):
    game = active_games[game_code]    

    emit('startGame', to=game_code) # Tell everyone in the room to start game
    game.status = 'waitingGameStart'

    setup_boards(game)
    
    pick_board(game)

    emit('newBoard', {'board': game.current_board}, to=game_code) # Tell everyone newBoard
    game.status = 'waitingForWord'



################
# HTTTP ROUTES #
################

@app.route('/ping')
def ping():
    return '', 204

@app.route('/check/<code>')
def check(code):
    if code in active_games.keys():
        # Game exists
        return '', 204
    else:
        # Game does not exist
        return 'Game not found', 404

####################
# SOCKET.IO EVENTS #
####################

@socket.on('createGame')
def create_game_event(json):
    new_game_code = generate_game_code()
    socket_id = request.sid
    new_game = Game(new_game_code, json, socket_id)
    active_games[new_game_code] = new_game
    join_room(new_game_code, socket_id)

    emit('createGameResponse', {'status': 201, 'gameCode': new_game_code}, to=socket_id)

@socket.on('joinGame')
def join_game_event(json):
    game_code = json['gameCode']
    game = active_games[game_code]
    name = json['name']
    socket_id = request.sid

    if not(game_code in active_games.keys()):
        emit('joinGameResponse', {'status': 404}, to=socket_id)
        disconnect(socket_id)
        return
    
    player = Player(socket_id, name)

    game.players.append(player)
    join_room(game_code, socket_id) # Add player to room

    emit('playerJoined', {'playerName', name}, to=game.host_socket_id) # Tell host that new player joined
    emit('joinGameResponse', {'status': 200}, to=socket_id) # Return 200 to new player

@socket.on('startGame')
def start_game_event(json):
    game_code = json['gameCode']
    socket_id = request.sid

    if not(game_code in active_games.keys()):
        emit('startGameResponse', {'status': 404}, to=socket_id)
        return
    else:
        game = active_games['game_code']
        host_socket_id = game.host_socket_id
        
        if host_socket_id != socket_id:
            # Not the host, return 403
            emit('startGameResponse', {'status': 403}, to=socket_id)
            return
    
    # Call start the game loop
    await game_loop(game_code)

app.run()
