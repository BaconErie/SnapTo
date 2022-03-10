const gameCodeWrapper = document.getElementById('game-code-wrapper');
const gameCodeForm = document.getElementById('game-code-form');
const gameCodeInput = document.getElementById('game-code-input');

const nameWrapper = document.getElementById('name-wrapper');
const nameForm = document.getElementById('name-form');
const nameInput = document.getElementById('name-input');

const lobbyWrapper = document.getElementById('lobby-wrapper');

const startingWrapper = document.getElementById('starting-wrapper');

const playWrapper = document.getElementById('play-wrapper');
const timer = document.getElementById('timer');
const message = document.getElementById('message');
const nameDisplay = document.getElementById('name');
const scoreDisplay = document.getElementById('display');
const termArea = document.getElementById('term-area');

const blankModal = document.getElementById('blank-answer-result-modal');
const blankResultWord = document.getElementById('blank-answer-result-word');
const blankResultImage = document.getElementById('blank-answer-result-image');

const correctModal = document.getElementById('correct-answer-result-modal');
const correctResultWord = document.getElementById('correct-answer-result-word');
const correctResultImage = document.getElementById('correct-answer-result-image');

const incorrectModal = document.getElementById('incorrect-answer-result-modal');
const incorrectResultWord = document.getElementById('incorrect-answer-result-word');
const incorrectResultImage = document.getElementById('incorrect-answer-result-image');
const pickedImage = document.getElementById('incorrect-answer-result-image');

var socket = io(SERVER_URL, {autoConnect: false});

var listeningForAnswers = false;
var answerElement;

var gameCode;

function pingServer(){
    fetch(`${SERVER_URL}/ping/`).then(response => {
        if(response.status != 204){
            switch(response.status){
                case 200:
                    break;

                case 503:
                    alert('Whoops! Looks like the server is not able start up. Please contact the developer with the error code: 503');
                    break;
                
                case 500:
                    alert('Uh oh, the server encountered a problem. Please try again later. If this problem persists, please contact the developer with the error code: 500');

                default:
                    alert('An unknown error occured. Please contact the developer with the time you encountered this problem and the error code + ' + response.status);
                    break;
            }
        }
    })
};

/***************
HELPER FUNCTIONS
***************/

async function countdown(seconds){
    let seconds_left = seconds - 1

    timer.innerHTML = seconds;

    let interval = setInterval(() => {
        if(seconds_left == 0){
            clearInterval(interval);
        }

        timer.innerHTML = seconds_left;
    }, 1000);
}

/********************
BUTTON EVENT HANDLERS
********************/

async function enterGameCodeEvent(){
    gameCode = gameCodeInput.value;

    let response = await fetch(`${SERVER_URL}/check/${gameCode}/`);
    if(response.status != 204 && response.status != 200){
        switch(response.status){
            case 404:
                alert('Hmm, we didn\'t find a game with that game code. Please check your game code and try again.')
                return;
                
            case 503:
                alert('Whoops! Looks like the server is not able start up. Please contact the developer with the error code: 503');
                return;
                
            case 500:
                alert('Uh oh, the server encountered a problem. Please try again later. If this problem persists, please contact the developer with the error code: 500');

            default:
                alert('An unknown error occured. Please contact the developer with the time you encountered this problem and the error code + ' + response.status);
                return;
        }
    }


    gameCodeWrapper.style.visibility = 'none';
    nameWrapper.style.visibility = 'block';
}

function joinGameEvent(){
    var name = nameInput.value;
    
    socket.connect();

    socket.emit('joinGame', {'gameCode': gameCode, 'name': name});
}

function chooseTermEvent(event){
    if(listeningForAnswers){
        let term = event.target;
        let termId = term.dataSet.termId;

        term.style.border
        listeningForAnswers = false;
        answerElement = term;
        socket.emit('chooseAnswer', {'gameCode': gameCode, 'answer': answer, 'termId': termId});

        term.classList.add('selected-answer');
    }
}

/********************
SOCKET IO CONNECTIONS
********************/

socket.on('joinGameResponse', (json) => {
    status = json['status']

    if(status != 200){
        switch(status){        
            case 404:
                alert('The game code you entered did not match any active games. Please check your game code and try again.');
                nameWrapper.style.visibility = 'none';
                gameCodeWrapper.style.visibility = 'block';
                break;

            case 401:
                alert('Someone already has that same name! Please pick a different name');
                break;
            
            default:
                alert('An unknown error occured. Please contact the developer with the time you encountered this problem and the error code + ' + status);
                break;
        }

        return;
    }

    nameWrapper.style.visibility = 'none';
    lobbyWrapper.style.visibility = 'block';
});

socket.on('startGame', (json) => {
    lobbyWrapper.style.visibility = 'none';
    startingWrapper.style.visibility = 'block';
    
});

socket.on('newBoard', (json) => {
    board = json['board'];

    // For start of game
    if(startingWrapper.style.visibility == 'block'){
        startingWrapper.style.visibility == 'none';
        playWrapper.style.visibility == 'block';
    }

    termTemplate = document.getElementById('term-TEMPLATE')
    for(index in board){
        term = board[index];
        url = term['url'];
        id = term['id'];
        x = term['x'];
        y = term['y'];
        newTerm = termTemplate.cloneNode(true);

        newTerm.dataSet.termId = id.tostring();
        newTerm.src = url;

        newTerm.style.left = x * (1/3)
        newTerm.style.top = y * (1/3)

        termArea.appendChild(newTerm)
    }
    
    message.innerHTML = 'Switching boards! Get ready...';
    countdown(3);
});

socket.on('newWord', (json) => {
    word = json['word'];
    listeningForAnswers = true;
    
    message.innerHTML = 'Current word: ' + word;
});

socket.on('countdown', (json) => {
    message.innerHTML = 'New word! Get ready...';
    countdown(3);
});

socket.on('answerResult', (json) => {
    let correct = json['correct'];
    let blank = json['blank'];
    let correctAnswer = json['correctAnswer'];
    let currentScore = json['currentScore'];

    if(blank){
        // 
        blankModal
    }
});