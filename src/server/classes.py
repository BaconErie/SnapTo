class Game:
    def __init__(self, game_code, terms, host):
        self.game_code = game_code
        self.players = []
        self.terms = []
        self.host_socket_id = host
        self.boards = []
        self.current_board = []
        self.words_displayed = 0
        self.current_word = ''
        self.terms_bucket = []
        self.listen_for_answers = False
        self.waiting_for_leaderboard = False

class Player:
    def __init__(self, socket_id, name, game):
        self.name = name
        self.socket_id = socket_id
        self.score = 0
        self.answer_chosen = None
        self.game = game
