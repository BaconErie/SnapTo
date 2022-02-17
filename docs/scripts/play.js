let gameCodeForm = document.getElementById('game-code-form');
let gameCodeInput = document.getElementById('game-code-input');

let nameForm = document.getElementById('name-form');
let nameInput = document.getElementById('name-input');

let socket = io(SERVER_URL, {autoConnect: false});

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

async function enterGameCode(){
    var gameCode = gameCodeInput.value;

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


    gameCodeForm.style.visibility = 'none';
    nameForm.style.visibility = 'block';
}
