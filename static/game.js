class CardGame {
    constructor(gameCode, playerId) {
        this.gameCode = gameCode;
        this.playerId = playerId;
        this.playerName = '';
        this.ws = null;
        this.selectedCards = new Set();
        this.setupWebSocket();
        this.setupEventListeners();

        // Check for saved game state
        const savedGame = localStorage.getItem('savedGame');
        if (savedGame) {
            const { gameCode, playerId } = JSON.parse(savedGame);
            this.rejoinGame(gameCode, playerId);
        }
    }

    rejoinGame(gameCode, playerId) {
        this.gameCode = gameCode;
        this.playerId = playerId;
        this.setupWebSocket();
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        this.ws = new WebSocket(`${protocol}//${host}/ws/${this.gameCode}/${this.playerId}`);
        
        this.ws.onopen = () => {
            const storedName = localStorage.getItem('playerName');
            if (!storedName) {
                this.promptForName();
            } else {
                this.playerName = storedName;
                this.sendAction('join', { name: storedName });
            }
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "gameState") {
                this.updateGameState(data.data);
            } else if (data.type === "announcement") {
                alert(data.message); // Display the announcement
            }
        };
    }

    promptForName() {
        const name = prompt("Enter your name:");
        if (name) {
            this.playerName = name;
            localStorage.setItem('playerName', name);
            this.sendAction('join', { name });
        }
    }

    updateGameState(state) {
        // Update game code
        document.getElementById('game-code').textContent = this.gameCode;

        // Update players list
        const playersList = document.getElementById('players-list');
        playersList.innerHTML = state.players.map(player => `
            <div class="player">
                <span class="player-name">${player.name}</span>
                <span class="player-lives">❤️</span>
            </div>
        `).join('');

        // Update current player's turn
        document.getElementById('current-player').textContent = state.current_player;

        // Update required card
        document.getElementById('required-type').textContent = state.required_card;

        // Show/hide start button for first player
        const startButton = document.getElementById('start-game');
        const isFirstPlayer = state.players.length > 0 && state.players[0].id === this.playerId;
        startButton.style.display = (isFirstPlayer && state.players.length >= 2 && !state.started) ? 'block' : 'none';

        if (state.started) {
            document.getElementById('waiting-room').style.display = 'none';
            document.getElementById('game-area').style.display = 'block';
            
            const playerState = state.players.find(p => p.id === this.playerId);
            if (playerState && playerState.cards) {
                this.displayCards(playerState.cards);
            }
        }
    }

    displayCards(cards) {
        const container = document.getElementById('cards-container');
        container.innerHTML = '';
        
        cards.forEach(card => {
            const cardElement = document.createElement('div');
            cardElement.className = 'card';
            cardElement.innerHTML = this.getCardSymbol(card.rank);
            cardElement.onclick = () => this.toggleCardSelection(cardElement, card);
            container.appendChild(cardElement);
        });
    }

    getCardSymbol(rank) {
        const symbols = {
            'K': '👑',
            'Q': '👸',
            'A': '🎯',
            'J': '🃏'
        };
        return symbols[rank] || rank;
    }

    setupEventListeners() {
        document.getElementById('start-game').onclick = () => {
            this.sendAction('start');
        };
    }

    sendAction(action, data = {}) {
        console.log('Sending action:', action, data); // Debug log
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action,
                ...data
            }));

            // Save game state in local storage
            if (action === 'join' || action === 'start') {
                localStorage.setItem('savedGame', JSON.stringify({
                    gameCode: this.gameCode,
                    playerId: this.playerId
                }));
            }
        }
    }

    playSelectedCards() {
        const selectedCards = Array.from(this.selectedCards);
        if (selectedCards.length === 0) {
            alert("You must select at least one card to play.");
            return;
        }
        if (selectedCards.length > 3) {
            alert("You can only play up to 3 cards.");
            return;
        }

        const claimRank = document.getElementById('claim-rank').value; // Get the claimed rank
        this.sendAction('play', { cards: selectedCards, claimRank });
        
        // Clear selected cards after sending
        this.selectedCards.clear();
        document.getElementById('play-selected').disabled = true; // Disable button until next selection
    }

    toggleCardSelection(cardElement, card) {
        console.log('Card clicked:', card.rank); // Debug log
        if (cardElement.classList.contains('selected')) {
            cardElement.classList.remove('selected');
            this.selectedCards.delete(card.rank);
        } else {
            if (this.selectedCards.size < 3) {
                cardElement.classList.add('selected');
                this.selectedCards.add(card.rank);
            }
        }
        
        console.log('Selected cards:', this.selectedCards); // Debug log
        document.getElementById('play-selected').disabled = this.selectedCards.size === 0;
    }

    endGame() {
        localStorage.removeItem('savedGame');
        // Additional logic to reset the game state can go here
    }
}

// Initialize the game
const game = new CardGame(gameCode, playerId);