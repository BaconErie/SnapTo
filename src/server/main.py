from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit, disconnect
from random import randint, sample
from classes import Player, Game
from time import sleep, time

app = Flask(__name__)
socket = SocketIO(app)
active_games = {}

def create_leaderboard(game):
    ### Create a leaderboard; a list of dictionaries with the player name and score
    leaderboard = []
    for player in game.players:
        current_player_dict = {}
        current_player_dict['name'] = player.name
        current_player_dict['score'] = player.score
        
        leaderboard.append(current_player_dict)

    # Sort the leaderboard so that the player with the highest score comes first
    leaderboard.sort(key=lambda d: d['score'], reverse=True)
    
    return leaderboard

def sort_players_by_score(game):
    '''Returns a list of player objects sorted by higher scoring first'''
    list_of_players = sorted(game.players, key=lambda player: player.score, reverse=True)

    return list_of_players

def get_place_on_leaderboard(player):
    game = player.game
    
    sorted_list_of_players = sort_players_by_score(game)
    place = sorted_list_of_players.index(player)

    return place

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
    
    # Loop through each board, then set the X and Y value of each term per board.
    for board in game.boards:
        for term in board:
            x = randint(1, 300)
            y = randint(1, 300)
            
            term['x'] = x
            term['y'] = y
    
    # Now check if there are terms that are overlapping
    for board in game.boards:
        for term in board:
            x = term['x']
            y = term['y']
            id = term['id']
            
            is_overlapping = True

            while is_overlapping:
                for term_compare in board:
                    if term_compare['id'] == id:
                        # Same term, skip/continue
                        continue
                    
                    if ((x <= (term_compare['x'] + 100)) and (x >= term_compare['x'])) and ((x <= (term_compare['y'] + 100)) and (x >= term_compare['y'])):
                        # Overlapping, change the current x and y values
                        term['x'] = randint(1, 300)
                        term['y'] = randint(1, 300)
                        
                        # Break this for loop and restart the checking
                        break
                    
                    # If we got here then the for loop was not broken
                    # Therefore there was no overlap
                    # Set is_overlapping to False
                    is_overlapping = False

def end_game(game_code):
    game = active_games[game_code]
    host_socket_id = game.host_socket_id
    # Send the host the sorted list of player names and scores
    leaderboard = create_leaderboard(game)

    emit('endGame', {'leaderboard': leaderboard}, to=host_socket_id)

    # Then loop through all the players and send them score and leaderboard place
    for player in game.players:
        place = get_place_on_leaderboard(player)
        emit('endGameScore', {'score': player.score, 'place': place}, to=player.socket_id)

    # Remove the game from the active games
    active_games.pop(game_code)

def pick_board(game):
    index = randint(0, len(game.boards))
    game.current_board = game.boards[index]
    game.boards.pop(index) # Remove the currently displayed board from boards

def start_game(game_code):
    game = active_games[game_code]    

    emit('startGame', to=game_code) # Tell everyone in the room to start game

    setup_boards(game)

def new_board(game_code):
    game = active_games[game_code]
    pick_board(game)

    # Set the game.word_bucket to the current word
    # The word bucket will be the list where we take terms from
    # We delete words we picked from the bucket
    game.word_bucket = game.current_board

    # Create a list of terms that only contain the id and image URL, not the answer
    board_to_send = []
    for term in game.current_board:
        filtered_term = {'id': term['id'], 'url': term['url']}
        board_to_send.append(filtered_term)

    emit('newBoard', {'board': board_to_send}, to=game_code) # Tell everyone newBoard

    game.words_displayed = 0

    sleep(3) # Give some time for players to look over the board

def new_word(game_code):
    game = active_games[game_code]

    index = randint(0, len(game.word_bucket) - 1)
    game.current_word = game.word_bucket[index]
    game.word_bucket.pop(index) # Deletes the word we have chosen


    countdown_end = time() + 3

    emit('countdown', to=game_code)
    sleep(3)

    game.listen_for_answers = True
    emit('newWord', {'word': game.current_word}, to=game_code)
    game.words_displayed = game.words_displayed + 1
    sleep(3)

    emit('stopAnswers', to=game_code)
    game.listen_for_answers = False

    for player in game.players:
        answer = player.answer_chosen
        socket_id = player.socket_id
        correct_answer_id = game.current_word['id']
        correct_answer = game.current_word
        
        if answer == None:
            emit('answerResult', {'correct': False, 'blank': True, 'correctAnswer': correct_answer, 'currentScore': player.score}, to=socket_id)        
        elif answer != correct_answer_id:
            emit('answerResult', {'correct': False, 'blank': False, 'correctAnswer': correct_answer, 'currentScore': player.score}, to=socket_id)
        elif answer == correct_answer_id:
            player.score = player.score + 100
            emit('answerResult', {'correct': True, 'blank': False, 'correctAnswer': correct_answer, 'currentScore': player.score}, to=socket_id)
            
        player.answer_chosen = None
    
    game.waiting_for_leaderboard = True
    
def show_leaderboard(game_code):
    game = active_games[game_code]
    
    leaderboard = create_leaderboard(game)

    emit('leaderboard', {'leaderboard': leaderboard}, to=game_code)

    game.waiting_for_leaderboard = False
    
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
    
    # Check if the name is a duplicate
    player = game.get_player_by_name(name)

    if player != None:
        # Player with that same name already exists
        emit('joinGameResponse', {'status': 409}, to=socket_id)
        disconnect(socket_id)
        return
    
    player = Player(socket_id, name, game)

    game.players.append(player)
    join_room(game_code, socket_id) # Add player to room

    emit('playerJoined', {'playerName', name}, to=game.host_socket_id) # Tell host that new player joined
    emit('joinGameResponse', {'status': 200}, to=socket_id) # Return 200 to new player

@socket.on('removePlayer')
def remove_player_event(json):
    game_code = json['gameCode']
    game = active_games[game_code]
    name_of_player = json['nameOfPlayer']
    socket_id = request.sid

    if not(game_code in active_games.keys()):
        emit('removePlayerResponse', {'status': 404}, to=socket_id)
        return
    else:
        game = active_games['game_code']
        host_socket_id = game.host_socket_id
        
        if host_socket_id != socket_id:
            # Not the host, return 403
            emit('removePlayerResponse', {'status': 403}, to=socket_id)
            return

    player = game.get_player_by_name(name_of_player)

    if player == None:
        emit('removePlayerResponse', {'status': 404, 'message': 'Player not found'}, to=socket_id)
        return

    # Remove the player from the Socket IO room
    leave_room(game_code, player.socket_id)

    game.players.remove(player)

    # Tell the player that you were removed from the game
    emit('playerRemoved', {'message': 'You were removed from the game'}, to=player.socket_id)

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


    start_game(game_code)
    new_board(game_code)
    new_word(game_code)

@socket.on('chooseAnswer')
def choose_answer_event(json):
    # Check if game exists
    if json['gameCode'] not in active_games.keys():
        emit('chooseAnswerResponse', {'status': 404, 'message': 'Game not found'}, to=request.sid)
        return

    game = active_games[json['gameCode']]
    player = game.get_player_by_socket_id(request.sid)
    answer = json['answer'] # Should be an id


    if not player:
        emit('chooseAnswerResponse', {'status': 401, 'message': 'You are not in the game'}, to=request.sid)
        return

    if player.answer_chosen != None:
        # Player already answered
        emit('chooseAnswerResponse', {'status': 409, 'message': 'You\'ve already answered'}, to=request.sid)
        return
    
    if not game.listen_for_answers:
        # Currently not listening for answers
        emit('chooseAnswerResponse', {'status': 400}, to=request.sid)
        return

    # Check if the answer id even exists
    term = game.get_term_by_id_from_current_board(answer)
    if term == None:
        emit('chooseAnswerResponse', {'status': 400}, to=request.sid)
        return
    
    player.answer_chosen = answer

@socket.on('showLeaderboard')
def show_leaderboard_event(json):
    game_code = json['gameCode']

    # Check if game exists
    if game_code not in active_games.keys():
        emit('nextWordResponse', {'status': 404, 'message': 'Game not found'}, to=request.sid)
        return
    
    game = active_games[game_code]
    if request.sid != game.host_socket_id:
        # Not the host, return 403
        emit('nextWordResponse', {'status': 403, 'message': 'You are not the host'}, to=request.sid)
        return

    if game.waiting_for_leaderboard:
            show_leaderboard(game_code)

@socket.on('nextWord')
def next_word_event(json):
    game_code = json['gameCode']

    # Check if game exists
    if game_code not in active_games.keys():
        emit('nextWordResponse', {'status': 404, 'message': 'Game not found'}, to=request.sid)
        return
    
    game = active_games[game_code]
    if request.sid != game.host_socket_id:
        # Not the host, return 403
        emit('nextWordResponse', {'status': 403, 'message': 'You are not the host'}, to=request.sid)
        return

    # Check if we should switch to the next board
    if game.words_displayed == 2:

        if len(game.boards) == 0:
            # Ran out of boards, end game
            end_game(game_code)
            return

        new_board(game_code)
    
    new_word(game_code)

@socket.on('endGameRequest')
def end_game_event(json):
    game_code = json['gameCode']
    socket_id = request.sid

    if not(game_code in active_games.keys()):
        emit('endGameResponse', {'status': 404}, to=socket_id)
        return
    else:
        game = active_games['game_code']
        host_socket_id = game.host_socket_id
        
        if host_socket_id != socket_id:
            # Not the host, return 403
            emit('endGameResponse', {'status': 403}, to=socket_id)
            return
    
    end_game(game_code)

socket.run(app)