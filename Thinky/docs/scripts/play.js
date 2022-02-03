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

/* CLIENT GAME CLASS */
class ClientGame{
    constructor(name, gameCode, socket){
        this.name = name;
        this.gameCode = gameCode;
        this.socket = socket;
        this.dataCurrentlyShown = {};
        this.currentTerm = null;
    }
    
    set currentlyShown(object){
        this.dataCurrentlyShown = object;
        for(let i in object){
            let termId = Object.keys(object)[i];
            let termX = object[i]['x'];
            let termY = object[i]['y'];
            let termSizeX = object[i]['sizeX'];
            let termSizeY = object[i]['sizeY'];
            let termImage = object[i]['image'];
            
            let term = document.createElement('img');
            term.id = termId;
            term.style.height = //FINISH THIS YOO
        }
    }
}

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
    //Otherwise, create a game object
            
})
