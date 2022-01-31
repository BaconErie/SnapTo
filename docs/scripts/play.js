/* GAME WRAPPERS */
const snapWrapper = document.getElementById('snap-wrapper');

/* MENUS */
const enterCode = document.getElementById('enter-code');
const enterName = document.getElementById('enter-name');
const connecting = document.getElementById('connecting');

/* COMPONENTS */
const enterCodeButton = document.getElementById('enter-code');
const gameCodeBox = document.getElementById('game-code');
const enterNameButton = document.getElementById('play');
const nameBox = document.getElementById('name');


/* SOCKET */
const socket = io(GAME_SERVER_URL, {autoConnect: false});

function checkCode(){
    let gameCode = gameCodeBox.value;

    // Send a get request to see if the game exists
    fetch(`${GAME_SERVER_URL}/check/${gameCode}`).then(response => {
        if(response.status != 200){
            // Something went wrong, see what exactly happened
            switch(response.status){
                case 404:
                    alert('Game not found. Please check your game pin and try again. Error 404');
                    break;
                
                case 500:
                    alert('Oops, we messed up! Please try again later. Error 500');
                    break;
                
                case 502:
                    alert('We were unable to connect to the main server. Please wait a few minutes and try again. Error 502');
                    break;
                
                case 504:
                    alert('We were unable to connect to the main server. Please wait a few minutes and try again. Error 504');
                    break;
                
                default:
                    alert(`An error occured. Please contact the dev with the error code: ${response.status}`);
                    break;
            }
        }else{
            // Otherwise, change menus
            enterCode.style.display = 'none';
            enterName.style.display = 'block';
        }
    });
}

function playGame(){
    let nameArg = nameBox.value;
    let gameCodeArg = gameCodeBox.value;

    enterName.style.display = 'none';
    connecting.style.display = 'block';

    socket.connect();

    socket.on('connect', () => {
        socket.emit('requestJoin', {gameCode: gameCodeArg, name: nameArg});
    });
}

socket.on('responseJoin', (json) => {
    connecting.style.display = 'none';
    if(json[code] != 200){
        enterCode.style.display = 'block';

        switch(json[code]){
            case 404:
                alert('Game not found. Please check your game pin and try again. Error 404');
                return;
        }
    }

    
})
